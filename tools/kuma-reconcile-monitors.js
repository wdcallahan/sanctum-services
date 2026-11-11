"use strict";
/* Uptime Kuma 2.5.9 Socket.IO, retained Kvin only. No direct SQLite edits. */
const fs=require("node:fs");
const {io}=require("socket.io-client");
const mode=process.argv[1];
if(!["reconcile","observe"].includes(mode)) process.exit(2);
const socket=io("http://127.0.0.1:3001",{transports:["websocket"],reconnection:false,timeout:8000});
const ack=(event,...args)=>new Promise((resolve,reject)=>socket.timeout(25000).emit(event,...args,(err,res)=>err?reject(new Error("ack_timeout")):resolve(res)));
const connected=()=>new Promise((resolve,reject)=>{
  if(socket.connected)return resolve();
  const t=setTimeout(()=>reject(new Error("connection_timeout")),10000);
  socket.once("connect",()=>{clearTimeout(t);resolve();});
  socket.once("connect_error",()=>{clearTimeout(t);reject(new Error("connection_error"));});
});
const expected={name:"Wicket Ollama",type:"http",method:"GET",url:"http://wicket.arcane.sanctum:11435/healthz",interval:60,accepted_statuscodes:["200-299"]};
function input(){
  const p=JSON.parse(fs.readFileSync(0,"utf8"));
  if(p.username!=="sanctum-admin"||typeof p.password!=="string"||!p.password.length)throw new Error("credentials_invalid");
  const m=p.monitor;
  if(!m||m.key!=="wicket_ollama"||m.name!==expected.name||m.type!==expected.type||m.method!==expected.method||m.url!==expected.url||Number(m.interval_seconds)!==60||JSON.stringify(m.accepted_status_codes)!=='["200-299"]'||m.intended_state!=="active_after_retained_kuma_acceptance")throw new Error("manifest_invalid");
  return p;
}
function matches(m){
  return m&&m.name===expected.name&&m.type===expected.type&&m.method===expected.method
    &&m.url===expected.url&&Number(m.interval)===60
    &&JSON.stringify(m.accepted_statuscodes)===JSON.stringify(expected.accepted_statuscodes)
    &&Boolean(m.active);
}
function noNotifications(m){
  if(Object.values(m?.notificationIDList||{}).some(Boolean))throw new Error("existing_notification_refused");
}
function desired(current){
  noNotifications(current);
  const managed={...expected,active:true,notificationIDList:{},retryInterval:60,maxretries:0,
    kafkaProducerBrokers:[],kafkaProducerSaslOptions:{mechanism:"None"},rabbitmqNodes:[],conditions:[]};
  return current?{...current,...managed,id:current.id}:{
    ...managed,parent:null,resendInterval:0,ignoreTls:false,
    expiryNotification:false,domainExpiryNotification:false,maxredirects:10,
    saveResponse:false,saveErrorResponse:true,
  };
}
function awaitList(){
  return new Promise((resolve,reject)=>{
    const t=setTimeout(()=>{socket.off("monitorList",handler);reject(new Error("list_timeout"));},25000);
    function handler(data){clearTimeout(t);resolve(data);}
    socket.once("monitorList",handler);
  });
}
async function getList(){
  const event=awaitList();
  const result=await ack("getMonitorList");
  if(!result?.ok)throw new Error("list_ack_failed");
  const all=await event;
  if(!all||Array.isArray(all)||typeof all!=="object")throw new Error("list_invalid");
  return Object.values(all);
}
async function getMonitor(id){
  const result=await ack("getMonitor",id);
  if(!result?.ok||!result.monitor||Number(result.monitor.id)!==Number(id))throw new Error("monitor_read_failed");
  return result.monitor;
}
async function main(){
  const p=input();await connected();
  const login=await ack("login",{username:p.username,password:p.password});
  if(!login?.ok)throw new Error("login_failed");
  if(mode==="observe"){
    // Kuma 2.5.9's own persisted heartbeat API; no synthetic curl
    // and no setup/add/edit/pause/resume events in this branch.
    const saved=await getMonitor(1);
    if(!matches(saved))throw new Error("saved_mismatch");
    noNotifications(saved);
    const beats=await ack("getMonitorBeats",1,1);
    if(!beats?.ok||!Array.isArray(beats.data))throw new Error("heartbeat_fetch_failed");
    const last=beats.data.length?beats.data[beats.data.length-1]:null;
    const code=last?Number(last.status):null;
    const rawTime=typeof last?.time==="string"?last.time:"";
    const normalized=rawTime.replace(" ","T");
    const timeMs=/^\\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d/.test(normalized)?
      Date.parse(/(?:Z|[+-]\\d\\d:\\d\\d)$/.test(normalized)?normalized:normalized+"Z"):NaN;
    const ageSeconds=Number.isFinite(timeMs)?Math.floor((Date.now()-timeMs)/1000):null;
    const recent=ageSeconds!==null&&ageSeconds>=-120&&ageSeconds<=180;
    const status=code===1?"Up":code===0?"Down":code===2?"Pending":code===3?"Maintenance":"Unknown";
    process.stdout.write(JSON.stringify({
      monitor_id:1,monitor_name:expected.name,persisted_configuration_verified:true,
      latest_status_in_kuma:status,heartbeat_records_last_hour:beats.data.length,
      heartbeat_age_seconds:ageSeconds,heartbeat_recent_within_180_seconds:recent,
      actual_up_accepted:recent&&code===1,
      notifications_attached:false,changed:false,
    })+"\\n");
    return;
  }
  const list=(await getList()).filter(m=>m?.name===expected.name);
  if(list.length>1)throw new Error("duplicate_monitor_refused");
  let id,action;
  if(!list.length){
    const r=await ack("add",desired(null));
    if(!r?.ok||!Number.isInteger(r.monitorID))throw new Error("add_failed");
    id=r.monitorID;action="created";
  }else{
    id=list[0].id;
    const current=await getMonitor(id);
    noNotifications(current);
    if(matches(current)){action="unchanged";}
    else{
      const r=await ack("editMonitor",desired(current));
      if(!r?.ok||Number(r.monitorID)!==Number(id))throw new Error("edit_failed");
      action="updated";
    }
  }
  const saved=await getMonitor(id);
  if(!matches(saved))throw new Error("saved_mismatch");
  noNotifications(saved);
  process.stdout.write(JSON.stringify({action,changed:action!=="unchanged",
    monitor_id:Number(id),monitor_name:expected.name,persisted_configuration_verified:true,
    notifications_attached:false,actual_up_accepted:false})+"\n");
}
main().catch(e=>{
  // Never include a server's raw error, passwords or tokens in output.
  const errors=new Set(["credentials_invalid","manifest_invalid","connection_timeout",
    "connection_error","ack_timeout","list_timeout","list_ack_failed","list_invalid",
    "login_failed","duplicate_monitor_refused","existing_notification_refused",
    "monitor_read_failed","add_failed","edit_failed","saved_mismatch","heartbeat_fetch_failed"]);
  process.stderr.write("Kuma monitor operation: "+(errors.has(e.message)?e.message:"unclassified")+"\n");
  process.exitCode=1;
}).finally(()=>socket.disconnect());
