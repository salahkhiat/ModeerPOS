from pathlib import Path
import ffmpeg

folder = Path("videos")

for mov_file in folder.glob("*"):
    if mov_file.suffix.lower() == ".mov":
        mp4_file = mov_file.with_suffix(".mp4")

        (
            ffmpeg
            .input(str(mov_file))
            .output(
                str(mp4_file),
                vcodec="libx264",
                acodec="aac",
                crf=18,
                preset="medium"
            )
            .overwrite_output()
            .run()
        )

        print(f"Converted: {mov_file.name} -> {mp4_file.name}")

print("Done!")