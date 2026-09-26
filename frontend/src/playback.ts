export type PlayTarget = {
  fileId: string;
  startTs: number;
  url: string;
};

export function createPlayerController(element: HTMLAudioElement) {
  let loadedFile = "";
  let chain: Promise<void> = Promise.resolve();

  return {
    play(target: PlayTarget): Promise<void> {
      const run = chain.then(async () => {
        element.pause();
        element.playbackRate = 1;
        if (loadedFile !== target.fileId) {
          loadedFile = target.fileId;
          element.src = target.url;
          await waitForMetadata(element);
        }
        element.currentTime = target.startTs;
        element.playbackRate = 1;
        await element.play();
      });
      chain = run.then(
        () => undefined,
        () => undefined,
      );
      return run;
    },
  };
}

function waitForMetadata(element: HTMLAudioElement): Promise<void> {
  if (element.readyState >= 1) {
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    const onReady = () => {
      cleanup();
      resolve();
    };
    const onError = () => {
      cleanup();
      reject(new Error("Audio failed to load"));
    };
    const cleanup = () => {
      element.removeEventListener("loadedmetadata", onReady);
      element.removeEventListener("error", onError);
    };
    element.addEventListener("loadedmetadata", onReady);
    element.addEventListener("error", onError);
  });
}
