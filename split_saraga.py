import os
import shutil
from pathlib import Path

# === INPUTS ===
original_base = Path("saraga audio")            # original dataset location
output_base = Path("saraga_audio_split")        # where to create train/test folders
train_artists_list = """
./Ashwin Srikant
./Amyea Karthikeyan
./Aditi Prahlad
./Hamzini
./Swarathmika
./Ashok Subramanyam
./Bhargavi Chandrashekar
./Vidya Kalyanaraman
./Manickam Yogeswaran
./Abhiram Bode
./Niranjan Dindodi
./Mukund Bharadwaj
./Hari Kishan
./Raghav Krishna
./Abhishek Ravishankar
./Chandana Bala
./Anjana Thirumalai
./Prithvi Harish
"""

# === PARSE TRAIN ARTISTS ===
train_artists = set(line.strip("./ ").strip() for line in train_artists_list.strip().splitlines())

# === CREATE OUTPUT DIRS ===
(output_base / "train").mkdir(parents=True, exist_ok=True)
(output_base / "test").mkdir(parents=True, exist_ok=True)

# === SPLIT LOGIC ===
for artist_dir in original_base.iterdir():
    if not artist_dir.is_dir():
        continue

    artist_name = artist_dir.name
    dest_split = "train" if artist_name in train_artists else "test"
    dest_path = output_base / dest_split / artist_name

    try:
        os.symlink(artist_dir.resolve(), dest_path, target_is_directory=True)
        print(f"✅ Linked {artist_name} → {dest_split}/")
    except FileExistsError:
        print(f"⚠️ Already exists: {dest_path}")
    except Exception as e:
        print(f"❌ Error linking {artist_name}: {e}")