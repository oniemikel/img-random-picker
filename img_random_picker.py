import os
import random
import shutil
from pathlib import Path
from dotenv import load_dotenv


def sample_images_per_folder(
    target_dir: str,
    output_dir: str = "annotation_samples",
    samples_per_folder: int = 3,
    preserve_hierarchy: bool = True,
    seed: int | None = None,
):
    if not target_dir:
        raise ValueError(
            "環境変数 TARGET_DIR が設定されていません。.env を確認してください。"
        )

    target_root = Path(target_dir).resolve()
    if not target_root.exists():
        raise FileNotFoundError(f"指定されたフォルダが見つかりません: {target_root}")

    output_root = Path(output_dir).resolve()

    if seed is not None:
        random.seed(seed)

    target_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    folder_count = 0
    skipped_count = 0
    total_copied = 0

    # 各階層フォルダを走査し、画像が含まれるフォルダごとにランダム抽出
    for dirpath, _, filenames in sorted(os.walk(target_root)):
        current_dir = Path(dirpath)
        images = sorted(
            current_dir / f for f in filenames if Path(f).suffix.lower() in target_exts
        )

        if not images:
            continue

        if preserve_hierarchy:
            rel_dir = current_dir.relative_to(target_root)
            dest_dir = output_root / rel_dir

            # すでに保存先ディレクトリが存在する場合はスキップ
            if dest_dir.exists():
                skipped_count += 1
                continue
        else:
            dest_dir = output_root

        k = min(samples_per_folder, len(images))
        picked_images = random.sample(images, k)

        dest_dir.mkdir(parents=True, exist_ok=True)

        for img_path in picked_images:
            dest_path = dest_dir / img_path.name
            shutil.copy2(img_path, dest_path)
            total_copied += 1

        folder_count += 1

    print(
        f"完了: {folder_count}個のフォルダから計 {total_copied}枚 を '{output_root}' にコピーしました。"
        f"（スキップ: {skipped_count}フォルダ）"
    )


if __name__ == "__main__":
    # .env ファイルから環境変数を読み込み
    load_dotenv()

    TARGET_DIR = os.getenv("TARGET_DIR")
    # .env に OUTPUT_DIR があればそれを使い、なければ "annotation_samples" を使用
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "annotation_samples")

    sample_images_per_folder(
        target_dir=TARGET_DIR,
        output_dir=OUTPUT_DIR,
        samples_per_folder=3,
        preserve_hierarchy=True,  # Roboflow等へ一括投入するため1フォルダにまとめたい場合は False に変更
        seed=42,  # 毎回違うランダム結果にしたい場合は None に変更
    )
