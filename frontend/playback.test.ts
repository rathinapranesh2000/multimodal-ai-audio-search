import { createPlayerController } from "./src/playback.ts";

class FakeAudio {
  playbackRate = 0;
  currentTime = 0;
  readyState = 0;
  src = "";
  playCalls = 0;
  inFlight = 0;
  maxInFlight = 0;
  seeks: number[] = [];
  rates: number[] = [];

  pause() {}

  play(): Promise<void> {
    this.playCalls += 1;
    this.inFlight += 1;
    this.maxInFlight = Math.max(this.maxInFlight, this.inFlight);
    this.rates.push(this.playbackRate);
    this.seeks.push(this.currentTime);
    return new Promise((resolve) => {
      setTimeout(() => {
        this.inFlight -= 1;
        resolve();
      }, 15);
    });
  }

  addEventListener(name: string, listener: () => void) {
    if (name === "loadedmetadata") {
      this.readyState = 1;
      listener();
    }
  }

  removeEventListener() {}
}

const audio = new FakeAudio();
const player = createPlayerController(audio as unknown as HTMLAudioElement);
const starts = [0, 64, 95, 127, 222];
const clicks = starts.map((startTs) =>
  player.play({ fileId: "one-file", startTs, url: "/api/audio/one-file" }),
);
await Promise.all(clicks);

if (audio.maxInFlight !== 1) {
  throw new Error(`play() overlapped: max in flight ${audio.maxInFlight}`);
}
if (audio.playCalls !== 5) {
  throw new Error(`expected 5 plays, got ${audio.playCalls}`);
}
if (audio.seeks.join(",") !== starts.join(",")) {
  throw new Error(`seeks ${audio.seeks.join(",")} did not match ${starts.join(",")}`);
}
if (audio.rates.some((rate) => rate !== 1)) {
  throw new Error(`playbackRate was not always 1: ${audio.rates.join(",")}`);
}
if (audio.src !== "/api/audio/one-file") {
  throw new Error("src was not reused for the same file");
}

console.log("5 rapid clicks: 1 player, play() never overlapped, each seek played at rate 1");
