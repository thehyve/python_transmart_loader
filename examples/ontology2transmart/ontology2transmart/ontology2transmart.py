import sys

import click

from .ontology_writer import OntologyWriter

from .dsv_reader import DsvReader
from transmart_loader.console import Console
from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.loader_exception import LoaderException


def read_chapters(chapters: str, writer: OntologyWriter) -> None:
    Console.info('Reading chapters from {}'.format(chapters))
    chapters_reader = DsvReader(chapters)
    for row in chapters_reader.reader:
        writer.process_chapter_row(row)


def read_groups(groups: str, writer: OntologyWriter) -> None:
    Console.info('Reading groups from {}'.format(groups))
    groups_reader = DsvReader(groups)
    for row in groups_reader.reader:
        writer.process_group_row(row)


def read_codes(codes: str, writer: OntologyWriter) -> None:
    Console.info('Reading codes from {}'.format(codes))
    codes_reader = DsvReader(codes)
    for row in codes_reader.reader:
        writer.process_code_row(row)


@click.command()
@click.argument('system')
@click.argument('chapters')
@click.argument('groups')
@click.argument('codes')
@click.argument('output_dir')
def ontology2transmart(system, chapters, groups, codes, output_dir):
    Console.title('Ontology to TranSMART')
    try:
        Console.info('Writing files to {}'.format(output_dir))
        copy_writer = TransmartCopyWriter(output_dir)
        ontology_writer = OntologyWriter(system)
        read_chapters(chapters, ontology_writer)
        read_groups(groups, ontology_writer)
        read_codes(codes, ontology_writer)
        ontology_writer.write(copy_writer)
        Console.info('Done.')
    except LoaderException as e:
        Console.error(e)
        sys.exit(1)


if __name__ == '__main__':
    ontology2transmart()
