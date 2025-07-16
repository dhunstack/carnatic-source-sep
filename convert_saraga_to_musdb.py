import os
from pathlib import Path
import soundfile as sf
import numpy as np

SRC_ROOT = Path("saraga audio")
DST_ROOT = Path("saraga_musdb")

def normalize(audio):
    peak = np.max(np.abs(audio))
    return audio / peak if peak > 1e-5 else audio

def load_and_trim(paths):
    audios = []
    sr = None
    for path in paths:
        audio, this_sr = sf.read(path)
        if sr is None:
            sr = this_sr
        elif sr != this_sr:
            raise ValueError(f"Sample rate mismatch in {path}")
        audios.append(audio)
    min_len = min([a.shape[0] for a in audios])
    audios = [normalize(a[:min_len]) for a in audios]
    return audios, sr

def process_track(comp_dir):
    comp_name = comp_dir.name
    artist = comp_dir.parent.name
    out_dir = DST_ROOT / f"{artist.replace(' ', '_')}_{comp_name.replace(' ', '_')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    def file(name): return comp_dir / f"{comp_name}.{name}.wav"

    paths = {
        "mix": comp_dir / f"{comp_name}.wav",
        "vocal": file("multitrack-vocal"),
        "violin": file("multitrack-violin"),
        "mrid_l": file("multitrack-mridangam-left"),
        "mrid_r": file("multitrack-mridangam-right"),
    }

    try:
        stems, sr = load_and_trim([paths["vocal"], paths["violin"], paths["mrid_l"], paths["mrid_r"]])
    except Exception as e:
        print(f"❌ Skipping {comp_dir}: {e}")
        return

    vocal, violin, mrid_l, mrid_r = stems
    mridangam = mrid_l + mrid_r
    nonvocal = violin + mridangam
    nonviolin = vocal + mridangam

    mix_audio, mix_sr = sf.read(paths["mix"])
    if mix_sr != sr:
        print(f"⚠️ Sample rate mismatch in mix: {paths['mix']}")
        return

    min_len = min(len(mix_audio), len(vocal))
    mix_audio = normalize(mix_audio[:min_len])

    vocal = vocal[:min_len]
    violin = violin[:min_len]
    mridangam = mridangam[:min_len]
    nonvocal = nonvocal[:min_len]
    nonviolin = nonviolin[:min_len]

    stem_wavs = {
        "mixture.wav": mix_audio,
        "vocal.wav": vocal,
        "violin.wav": violin,
        "mridangam.wav": mridangam,
        "nonvocal.wav": nonvocal,
        "nonviolin.wav": nonviolin,
    }

    for name, data in stem_wavs.items():
        out_path = out_dir / name
        sf.write(out_path, data, sr)
        print(f"✅ Saved {out_path}")

def main():
    for artist_dir in SRC_ROOT.iterdir():
        if not artist_dir.is_dir():
            continue
        for comp_dir in artist_dir.iterdir():
            if not comp_dir.is_dir():
                continue
            process_track(comp_dir)

if __name__ == "__main__":
    main()
