let ltDecoder = null;

let currentStatus = 0; // 0: idle; 1: in progress; 2: finished
let receivedChunks = 0;
let totalChunks = 0;

var video = document.createElement("video");
var canvasElement = document.getElementById("canvas");
var canvas = canvasElement.getContext("2d");
var loadingMessage = document.getElementById("loadingMessage");
var outputContainer = document.getElementById("output");
var outputMessage = document.getElementById("outputMessage");
var progressBar = document.getElementById("progressBar");

// Use facingMode: environment to attempt to get the front camera on phones
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function (stream) {
  video.srcObject = stream;
  video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
  video.play();
  requestAnimationFrame(tick);
});

function tick() {
  loadingMessage.innerText = "⌛ Loading video..."
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    loadingMessage.hidden = true;
    canvasElement.hidden = false;
    if (currentStatus === 0) outputContainer.hidden = false;

    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
    var imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
    var code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: "dontInvert",
    });
    if (code && currentStatus < 2) {
      // drawBoundBox(code)

      parseChunk(code.binaryData);

      if (currentStatus === 1) {
        outputContainer.hidden = true;
        progressBar.hidden = false;
        progressBar.ariaValueMin = 0;
        progressBar.ariaValueNow = receivedChunks;
        progressBar.ariaValueMax = totalChunks;
        progressBar.children[0].style.width = `${(receivedChunks / totalChunks * 100).toFixed(0)}%`;
        progressBar.children[0].innerHTML = `${receivedChunks} / ${totalChunks}`;
      } else if (currentStatus === 2) {
        video.pause();
        outputMessage.innerText = "FINISHED!";
        outputContainer.hidden = false;
        progressBar.hidden = true;
        downloadFile(ltDecoder.decodedData);
      }
    }
  }
  requestAnimationFrame(tick);
}

function parseChunk(data) {
  if (data.length <= 13) return;
  const dataView = new DataView((new Uint8Array(data)).buffer);
  const not_naive = dataView.getUint8(0);
  const total_chunks = dataView.getUint32(1, false);
  const seed = dataView.getUint32(5, false);
  const n_lt_samples = dataView.getUint32(9, false);

  if (currentStatus == 0) {
    currentStatus = 1;
    receivedChunks = 0;
    totalChunks = total_chunks;
    ltDecoder = new LTDecoder(totalChunks);
  }

  const rng = new MersenneTwister();
  rng.init_genrand(seed);
  const sampledIdx = not_naive ? rng.genrand_sample(totalChunks, n_lt_samples) : [seed];
  let raw_data = data.slice(13);

  ltDecoder.decode({ seed: seed, idxList: sampledIdx, data: raw_data });

  receivedChunks = ltDecoder.decoded();

  if (ltDecoder.finished()) {
    currentStatus = 2;
  }
}