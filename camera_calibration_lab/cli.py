from __future__ import annotations

import argparse
from pathlib import Path

from .boards import ChessboardSpec
from .io_utils import write_json
from .mono import calibrate_mono
from .stereo import calibrate_stereo
from .visualization import batch_visualize_corners, visualize_corners, visualize_undistort


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {'true', '1', 'yes', 'y'}:
        return True
    if normalized in {'false', '0', 'no', 'n'}:
        return False
    raise argparse.ArgumentTypeError('expected true or false')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Camera calibration lab')
    subparsers = parser.add_subparsers(dest='command', required=True)

    mono_parser = subparsers.add_parser('mono', help='run mono calibration')
    mono_parser.add_argument('--images', type=Path, required=True, help='mono image directory')
    mono_parser.add_argument('--rows', type=int, required=True, help='chessboard inner corner rows')
    mono_parser.add_argument('--cols', type=int, required=True, help='chessboard inner corner cols')
    mono_parser.add_argument('--square-size', type=float, required=True, help='square size in your chosen unit')
    mono_parser.add_argument('--output', type=Path, required=True, help='output json path')

    stereo_parser = subparsers.add_parser('stereo', help='run stereo calibration')
    stereo_parser.add_argument('--left-images', type=Path, required=True, help='left image directory')
    stereo_parser.add_argument('--right-images', type=Path, required=True, help='right image directory')
    stereo_parser.add_argument('--rows', type=int, required=True, help='chessboard inner corner rows')
    stereo_parser.add_argument('--cols', type=int, required=True, help='chessboard inner corner cols')
    stereo_parser.add_argument('--square-size', type=float, required=True, help='square size in your chosen unit')
    stereo_parser.add_argument('--output', type=Path, required=True, help='output json path')

    corners_parser = subparsers.add_parser('visualize-corners', help='visualize detected chessboard corners')
    corners_parser.add_argument('--image', type=Path, required=True, help='input image path')
    corners_parser.add_argument('--rows', type=int, required=True, help='chessboard inner corner rows')
    corners_parser.add_argument('--cols', type=int, required=True, help='chessboard inner corner cols')
    corners_parser.add_argument('--square-size', type=float, required=True, help='square size in your chosen unit')
    corners_parser.add_argument('--output', type=Path, required=True, help='output image path')

    batch_corners_parser = subparsers.add_parser('batch-visualize-corners', help='export chessboard corner previews for all images in a directory')
    batch_corners_parser.add_argument('--images', type=Path, required=True, help='input image directory')
    batch_corners_parser.add_argument('--rows', type=int, required=True, help='chessboard inner corner rows')
    batch_corners_parser.add_argument('--cols', type=int, required=True, help='chessboard inner corner cols')
    batch_corners_parser.add_argument('--square-size', type=float, required=True, help='square size in your chosen unit')
    batch_corners_parser.add_argument('--output-dir', type=Path, required=True, help='directory for annotated images')
    batch_corners_parser.add_argument('--summary', type=Path, required=True, help='summary json path')
    batch_corners_parser.add_argument('--visualize', type=parse_bool, default=True, help='whether to export annotated images: true or false')

    undistort_parser = subparsers.add_parser('visualize-undistort', help='visualize original and undistorted image')
    undistort_parser.add_argument('--image', type=Path, required=True, help='input image path')
    undistort_parser.add_argument('--calibration', type=Path, required=True, help='calibration json path')
    undistort_parser.add_argument('--output', type=Path, required=True, help='output image path')
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'mono':
        board = ChessboardSpec(rows=args.rows, cols=args.cols, square_size=args.square_size)
        result = calibrate_mono(args.images, board)
        write_json(args.output, result.as_dict())
        print(f'mono calibration done: {args.output}')
        print(f'total images: {result.total_images}')
        print(f'valid images: {result.valid_images}')
        print(f'rejected images: {len(result.rejected_images)}')
        print(f'reprojection error: {result.reprojection_error:.6f}')
        return

    if args.command == 'stereo':
        board = ChessboardSpec(rows=args.rows, cols=args.cols, square_size=args.square_size)
        result = calibrate_stereo(args.left_images, args.right_images, board)
        write_json(args.output, result.as_dict())
        print(f'stereo calibration done: {args.output}')
        print(f'total pairs: {result.total_pairs}')
        print(f'valid pairs: {result.valid_pairs}')
        print(f'rejected pairs: {len(result.rejected_pairs)}')
        print(f'stereo error: {result.stereo_error:.6f}')
        return

    if args.command == 'visualize-corners':
        board = ChessboardSpec(rows=args.rows, cols=args.cols, square_size=args.square_size)
        found = visualize_corners(args.image, board, args.output)
        print(f'chessboard found: {found}')
        print(f'corner visualization saved: {args.output}')
        return

    if args.command == 'batch-visualize-corners':
        board = ChessboardSpec(rows=args.rows, cols=args.cols, square_size=args.square_size)
        summary = batch_visualize_corners(args.images, board, args.output_dir, args.summary, args.visualize)
        print(f"processed images: {summary['total_images']}")
        print(f"successful detections: {summary['success_count']}")
        print(f"failed detections: {summary['failure_count']}")
        print(f"visualize: {summary['visualize']}")
        if args.visualize:
            print(f'corner previews saved: {args.output_dir}')
        print(f'summary saved: {args.summary}')
        return

    visualize_undistort(args.image, args.calibration, args.output)
    print(f'undistort visualization saved: {args.output}')


if __name__ == '__main__':
    main()
