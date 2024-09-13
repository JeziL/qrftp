function xorBlocks(block1, block2) {
  const length = Math.min(block1.length, block2.length);
  const result = new Uint8Array(length);
  for (let i = 0; i < length; i++) {
    result[i] = block1[i] ^ block2[i];
  }
  return result;
}

function downloadFile(decodedData) {
  const InvalidChunkException = {};
  let file_ext = ".bin";
  try {
    decodedData.forEach(d => {
      let pipeIndex = -1;
      for (let i = 0; i < d.c.length; i++) {
        if (d.c[i] === 124) { // ASCII code for '|'
          pipeIndex = i;
          break;
        }
      }
      if (pipeIndex === -1) {
        throw InvalidChunkException;
      }
      file_ext = String.fromCharCode.apply(null, d.c.slice(0, pipeIndex));
      if (d.c.length < pipeIndex + 4) {
        throw InvalidChunkException;
      }
      const dataLen = d.c[pipeIndex + 1] * 0x100 + d.c[pipeIndex + 2];
      if (d.c.length < pipeIndex + dataLen + 3) {
        throw InvalidChunkException;
      }
      d.c = Array.from(d.c.slice(pipeIndex + 3, pipeIndex + dataLen + 3));
    });
  } catch (e) {
    alert("Invalid chunk!");
    return;
  }
  
  decodedData.sort((a, b) => a.idx - b.idx);
  const result = decodedData.map(d => d.c).flat();
  const fileData = new Uint8ClampedArray(result);
  const blob = new Blob([fileData.buffer], { type: 'application/octet-stream' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `file${file_ext}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function drawLine(begin, end, color) {
  canvas.beginPath();
  canvas.moveTo(begin.x, begin.y);
  canvas.lineTo(end.x, end.y);
  canvas.lineWidth = 4;
  canvas.strokeStyle = color;
  canvas.stroke();
}

function drawBoundBox(code) {
  drawLine(code.location.topLeftCorner, code.location.topRightCorner, "#FF3B58");
  drawLine(code.location.topRightCorner, code.location.bottomRightCorner, "#FF3B58");
  drawLine(code.location.bottomRightCorner, code.location.bottomLeftCorner, "#FF3B58");
  drawLine(code.location.bottomLeftCorner, code.location.topLeftCorner, "#FF3B58");
}
