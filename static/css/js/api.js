 
 const API = 'http://127.0.0.1:5000';
 
 export async function getJSON(url) {
    const res = await fetch(API + url);
    return res.json();
}