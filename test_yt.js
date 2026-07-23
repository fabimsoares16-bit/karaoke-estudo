async function run() {
  try {
    const res = await fetch('https://yewtu.be/api/v1/search?q=hello+adele+audio');
    const data = await res.json();
    console.log(data[0].videoId);
  } catch(e) {
    console.error(e);
  }
}
run();
