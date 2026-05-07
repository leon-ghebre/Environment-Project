 
 const API = 'http://127.0.0.1:5000';
 
 export async function getJSON(url) {
    const res = await fetch(API + url);
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status} for ${url}: ${text}`);
    }
    return res.json();
}