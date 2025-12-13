import fs from 'fs';
import fetch from 'node-fetch';
import path from 'path';

const CLIENT_ID = process.env.OSU_CLIENT_ID;
const CLIENT_SECRET = process.env.OSU_CLIENT_SECRET;
const COUNTRY = "IQ";
const MODE = "osu";

// Helper
function mkdirp(dir){if(!fs.existsSync(dir)) fs.mkdirSync(dir,{recursive:true});}
function today(){return new Date().toISOString().split('T')[0];}

async function getToken(){
  const res = await fetch('https://osu.ppy.sh/oauth/token',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({client_id:CLIENT_ID,client_secret:CLIENT_SECRET,grant_type:'client_credentials',scope:'public'})
  });
  return (await res.json()).access_token;
}

async function main(){
  const token = await getToken();
  const headers = {Authorization:`Bearer ${token}`};

  // Get top Iraqi players
  const rankingRes = await fetch(`https://osu.ppy.sh/api/v2/rankings/${MODE}/performance?country=${COUNTRY}`,{headers});
  const rankingData = await rankingRes.json();
  const users = rankingData.ranking.slice(0,10);

  let scores=[];

  for(const u of users){
    const res = await fetch(`https://osu.ppy.sh/api/v2/users/${u.user.id}/scores/recent?limit=5`,{headers});
    const data = await res.json();
    data.forEach(s=>{
      scores.push({
        user:u.user.username,
        user_id:u.user.id,
        country:COUNTRY,
        score_id:s.id,
        rank:s.rank,
        accuracy:s.accuracy,
        pp:s.pp,
        mods:s.mods,
        combo:s.max_combo,
        created_at:s.created_at,
        beatmapset:{id:s.beatmapset.id,title:s.beatmapset.title,cover:s.beatmapset.covers.card}
      });
    });
  }

  // Sort newest first
  scores.sort((a,b)=>new Date(b.created_at)-new Date(a.created_at));

  // Save daily file
  const dateParts = today().split('-');
  const dir = path.join('data', dateParts[0], dateParts[1]);
  mkdirp(dir);
  fs.writeFileSync(path.join(dir,dateParts[2]+'.json'),JSON.stringify({
    date:today(),
    country:COUNTRY,
    generated_at:new Date().toISOString(),
    scores
  },null,2));

  // Update index.json
  const indexFile = path.join('data','index.json');
  let indexData={available_dates:[]};
  if(fs.existsSync(indexFile)) indexData=JSON.parse(fs.readFileSync(indexFile));
  if(!indexData.available_dates.includes(today())) indexData.available_dates.push(today());
  fs.writeFileSync(indexFile,JSON.stringify(indexData,null,2));

  console.log('Daily archive updated for',today());
}

main();
