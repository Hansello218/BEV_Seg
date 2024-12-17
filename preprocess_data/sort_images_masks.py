import os
import shutil
import argparse
from tqdm import tqdm


def sort_rgb_images(images_dir):
    # Get list of image files
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]

    # Sort the image files based on extracted image index
    image_files.sort(key=lambda x: (extract_first_index(x), extract_second_index(x)))

    return image_files


def extract_first_index(filename):
    """
    Extracts the first index from the filename.
    Assumes the filename format is like 'BEV_1_full_sub_1.jpg'.
    """
    index_str = filename.split('_')[1]
    if 'BEV' in index_str:
        index_str = index_str.replace('BEV', '')
    return int(index_str) if index_str.isdigit() else 0

def extract_second_index(filename):
    """
    Extracts the second index from the filename.
    Assumes the filename format is like 'BEV_1_full_sub_1.jpg'.
    """
    index_str = filename.split('_')[-1].split('.')[0]
    return int(index_str) if index_str.isdigit() else 0


def integrate_datasets(root_dir, rgb_output_dir, mask_output_dir):
    if not os.path.exists(rgb_output_dir):
        os.makedirs(rgb_output_dir)
    if not os.path.exists(mask_output_dir):
        os.makedirs(mask_output_dir)

    total_images = 0
    for subdir in sorted(os.listdir(root_dir)):
        subdir_path = os.path.join(root_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue

        for subsubdir in sorted(os.listdir(subdir_path)):
            subsubdir_path = os.path.join(subdir_path, subsubdir)
            if not os.path.isdir(subsubdir_path):
                continue

            images_dir = os.path.join(subsubdir_path, 'images')
            masks_dir = os.path.join(subsubdir_path, 'mask_output')

            if os.path.exists(images_dir) and os.path.exists(masks_dir):
                total_images += len([f for f in os.listdir(images_dir) if f.endswith('.jpg')])

    # Use tqdm for progress visualization
    progress_bar = tqdm(total=total_images, desc='Processing')

    # Initialize counter for the processed RGB images
    processed_rgb_images = 0

    for subdir in sorted(os.listdir(root_dir)):
        subdir_path = os.path.join(root_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue

        for subsubdir in sorted(os.listdir(subdir_path)):
            subsubdir_path = os.path.join(subdir_path, subsubdir)
            if not os.path.isdir(subsubdir_path):
                continue

            images_dir = os.path.join(subsubdir_path, 'images')
            masks_dir = os.path.join(subsubdir_path, 'mask_output')

            if os.path.exists(images_dir) and os.path.exists(masks_dir):
                # Sort RGB images
                rgb_image_files = sort_rgb_images(images_dir)

                # Collect mask images
                mask_image_paths = [os.path.join(masks_dir, f) for f in sorted(os.listdir(masks_dir)) if
                                    f.startswith('mask_') and f.endswith('.png')]

                # Match RGB images with mask images based on index
                for i, (rgb_image_file, mask_image_path) in enumerate(zip(rgb_image_files, mask_image_paths),
                                                                      start=processed_rgb_images):
                    new_rgb_name = f"mask{i}.jpg"
                    new_mask_name = f"mask{i}.png"
                    shutil.copy(os.path.join(images_dir, rgb_image_file), os.path.join(rgb_output_dir, new_rgb_name))
                    shutil.copy(mask_image_path, os.path.join(mask_output_dir, new_mask_name))

                    # Update processed RGB images counter
                    processed_rgb_images += 1

                    # Update progress
                    progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()


def main():
    parser = argparse.ArgumentParser(description='Integrate datasets into a single dataset.')
    parser.add_argument('root_dir', help='Root directory containing multiple datasets')
    parser.add_argument('rgb_output_dir', help='Output directory for RGB images')
    parser.add_argument('mask_output_dir', help='Output directory for mask images')
    args = parser.parse_args()

    integrate_datasets(args.root_dir, args.rgb_output_dir, args.mask_output_dir)


if __name__ == "__main__":
    main()
