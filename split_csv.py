import argparse
import csv


def split_csv(
    source_file: str,
    chunk_size: int,
    out_file_template: str,
    delimiter: str = ',',
):
    """Split a CSV file into N files of particular chunk size.
    Args:
        source_file (str): Path to source file.
        chunk_size (int): Number of rows in each new file.
        out_file_template (str): Template for output files naming.
            Example: `data%03d.csv`.
        delimiter (str): Delimiter used in source and result files.
    """
    # Number of current chunk
    current_chunk = 0

    with open(source_file) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        headers = next(csv_reader)
        out_writer = None

        for i, row in enumerate(csv_reader):
            if i % chunk_size == 0:
                current_chunk += 1
                result_file = out_file_template % current_chunk
                out_writer = csv.writer(
                    open(result_file, 'w'),
                    delimiter=delimiter,
                )
                out_writer.writerow(headers)
                print(f'File {result_file} created')

            out_writer.writerow(row)

        print(f'Done. {current_chunk} file created.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--source-file',
        help='Path to source file.',
    )
    parser.add_argument(
        '--chunk-size',
        help='Number of rows in each new chunk.',
        type=int,
    )
    parser.add_argument(
        '--out-file-template',
        help='Template for output files naming. Example: `data%03d.csv`.',
    )
    parser.add_argument(
        '--delimiter',
        help='Delimiter used in source and result files. "," by default.',
        default=',',
    )

    args = parser.parse_args()

    split_csv(
        source_file=args.source_file,
        chunk_size=args.chunk_size,
        out_file_template=args.out_file_template,
        delimiter=args.delimiter,
    )
