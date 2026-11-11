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
    id:7,name:"Wicket Ollama",type:"http",method:"GET",
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
const run=(vars={})=>child.spawnSync(process.execPath,["-e",code,"reconcile"],{
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
  console.log("PASS: native Kuma monitor Socket.IO source create/unchanged/edit/duplicate/auth failure");
}finally{fs.rmSync(tmp,{recursive:true,force:true});}
