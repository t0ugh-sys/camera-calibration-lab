from __future__ import annotations

import argparse
from pathlib import Path

from .boards import ChessboardSpec
from .io_utils import write_json
from .mono import calibrate_mono
from .stereo import calibrate_stereo


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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    board = ChessboardSpec(rows=args.rows, cols=args.cols, square_size=args.square_size)

    if args.command == 'mono':
        result = calibrate_mono(args.images, board)
        write_json(args.output, result.as_dict())
        print(f'mono calibration done: {args.output}')
        return

    result = calibrate_stereo(args.left_images, args.right_images, board)
    write_json(args.output, result.as_dict())
    print(f'stereo calibration done: {args.output}')


if __name__ == '__main__':
    main()
