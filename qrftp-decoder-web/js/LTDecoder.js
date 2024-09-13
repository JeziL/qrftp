/** Derived from https://github.com/mwdchang/fountain-code/blob/master/fountain.js */

class LTDecoder {
  constructor(totalChunks) {
    this.reserve = [];
    this.decodedData = Array.from(Array(totalChunks).keys()).map((i) => ({ c: null, idx: i }));
  }

  finished() {
    return (_.some(this.decodedData, d => d.c === null) === false);
  }

  decoded() {
    return this.decodedData.filter(d => d.c !== null).length;
  }

  resolve(c, idx) {
    if (this.decodedData[idx].c !== null) return;

    this.decodedData[idx].c = c;
    this.reserve.forEach(p => {
      if (p.idxList.indexOf(idx) >= 0) {
        p.data = xorBlocks(p.data, c);
        p.idxList = _.difference(p.idxList, [idx]);
      }
    });

    let newResolve = _.remove(this.reserve, p => p.idxList.length === 1);
    newResolve.forEach(p => {
      this.resolve(p.data, p.idxList[0]);
    });
  }

  decode(packet) {
    let reserve = this.reserve;

    if (_.some(reserve, d => (d.seed === packet.seed))) return;

    let decoded = this.decodedData.filter(d => d.c !== null);
    decoded.forEach(d => {
      if (packet.idxList.indexOf(d.idx) >= 0) {
        packet.data = xorBlocks(packet.data, d.c);
        packet.idxList = _.difference(packet.idxList, [d.idx]);
      }
    });

    if (packet.idxList.length === 0) return;

    if (packet.idxList.length === 1) {
      this.resolve(packet.data, packet.idxList[0]);
    } else {
      this.reserve.push(packet);
    }
  }
}
