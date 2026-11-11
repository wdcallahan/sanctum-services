"use strict";
/* Real node execution with fake Socket.IO transport, no network access. */
const fs=require("node:fs"),os=require("node:os"),path=require("node:path");
const child=require("node:child_process"),assert=require("node:assert/strict");
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),"kuma-monitor-source-"));
const lib=path.join(tmp,"socket.io-client");fs.mkdirSync(lib,{recursive:true});
fs.writeFileSync(path.join(lib,"index.js"),`
const EventEmitter=require("node:events");
module.exports.io=function(){
  const s=new EventEmitter();s.connected=false;s.timeout=()=>s;s.disconnect=()=>{};
  let existing=process.env.CURRENT==="none"?null:{
    id:process.env.MODEL_ID1==="1"?1:7,name:"Wicket Ollama",type:"http",method:"GET",
    url:process.env.CURRENT==="wrong"?"http://wrong.invalid": "http://wicket.arcane.sanctum:11435/healthz",
    interval:60,accepted_statuscodes:["200-299"],active:true,notificationIDList:{},
    kafkaProducerBrokers:[],kafkaProducerSaslOptions:{mechanism:"None"},
    rabbitmqNodes:[],conditions:[]
  };
  const original=s.emit.bind(s);
  s.emit=(event,...args)=>{
    const cb=args[args.length-1];
    if(event==="login") cb(null,{ok:process.env.BAD_LOGIN!=="1",token:"DONT-LOG"});
    else if(event==="getMonitorList"){
      process.nextTick(()=>original("monitorList",existing?{7:existing}:{}));cb(null,{ok:true});
    }
    else if(event==="getMonitor") cb(null,{ok:true,monitor:existing});
    else if(event==="getMonitorBeats"){
      const offset=process.env.OLD_BEAT==="1"?300000:45000;
      const time=new Date(Date.now()-offset).toISOString().replace("T"," ").replace("Z","");
      cb(null,{ok:true,data:process.env.NO_BEATS==="1"?[]:[{time,status:Number(process.env.BEAT_STATUS||"1")}]});
    }
    else if(event==="add") {
      existing={...args[0],id:7};
      cb(null,{ok:true,monitorID:7});
    }
    else if(event==="editMonitor") {
      existing={...args[0],id:7};
      cb(null,{ok:true,monitorID:7});
    }
    else original(event,...args);
    return s;
  };
  if(process.env.DUPLICATE==="1"){
    const base=s.emit.bind(s);
    s.emit=(event,...args)=>{
      if(event==="getMonitorList"){
        process.nextTick(()=>original("monitorList",{7:existing,8:{...existing,id:8}}));
        args[args.length-1](null,{ok:true});return s;
      }
      return base(event,...args);
    }
  }
  process.nextTick(()=>{s.connected=true;original("connect");});
  return s;
}
`);
const code=fs.readFileSync(path.join(__dirname,"../../tools/kuma-reconcile-monitors.js"),"utf8");
const input=JSON.stringify({username:"sanctum-admin",password:"a-user-chosen-secret",
  monitor:{key:"wicket_ollama",name:"Wicket Ollama",type:"http",method:"GET",
    url:"http://wicket.arcane.sanctum:11435/healthz",interval_seconds:60,
    accepted_status_codes:["200-299"],intended_state:"active_after_retained_kuma_acceptance"}});
const run=(vars={},mode="reconcile")=>child.spawnSync(process.execPath,["-e",code,mode],{
  encoding:"utf8",input,timeout:7000,env:{...process.env,NODE_PATH:tmp,...vars}});
try {
  for(const [env,expected] of [[{CURRENT:"none"},"created"],[{CURRENT:"correct"},"unchanged"],[{CURRENT:"wrong"},"updated"]]){
    const out=run(env);
    assert.equal(out.status,0,out.stderr);
    const msg=JSON.parse(out.stdout);
    assert.equal(msg.action,expected);
    assert.equal(msg.changed,expected!=="unchanged");
    assert.equal(msg.persisted_configuration_verified,true);
    assert.equal(msg.actual_up_accepted,false);
    assert.equal(msg.notifications_attached,false);
  }
  for(const env of [{CURRENT:"correct",DUPLICATE:"1"},{CURRENT:"correct",BAD_LOGIN:"1"}]){
    const out=run(env);assert.notEqual(out.status,0);
    assert.ok(!out.stdout.includes("a-user-chosen-secret"));
    assert.ok(!out.stderr.includes("a-user-chosen-secret"));
  }
  for(const [env,status,up,recent] of [
    [{BEAT_STATUS:"1"},"Up",true,true],
    [{BEAT_STATUS:"0"},"Down",false,true],
    [{BEAT_STATUS:"2"},"Pending",false,true],
    [{NO_BEATS:"1"},"Unknown",false,false],
    [{OLD_BEAT:"1"},"Up",false,false],
  ]){
    const r=run({CURRENT:"correct",MODEL_ID1:"1",...env},"observe");
    assert.equal(r.status,0,r.stderr);
    const data=JSON.parse(r.stdout);
    assert.equal(data.changed,false);
    assert.equal(data.actual_up_accepted,up);
    assert.equal(data.latest_status_in_kuma,status);
    assert.equal(data.heartbeat_recent_within_180_seconds,recent);
    assert.ok(!r.stdout.includes("a-user-chosen-secret"));
  }
  const rejected=run({CURRENT:"correct",MODEL_ID1:"1",BAD_LOGIN:"1"},"observe");
  assert.notEqual(rejected.status,0);
  assert.ok(!rejected.stdout.includes("a-user-chosen-secret"));
  assert.ok(!rejected.stderr.includes("a-user-chosen-secret"));
  console.log("PASS: Kuma native monitor create/unchanged/edit/duplicate/auth and actual heartbeat Up/Down/Pending/stale/missing");
}finally{fs.rmSync(tmp,{recursive:true,force:true});}
