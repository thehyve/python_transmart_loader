import json
import os
import sys
from os import path

import click

from .fhir_reader import FhirReader
from .mapper import Mapper
from transmart_loader.console import Console
from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.loader_exception import LoaderException


@click.command()
@click.argument('input')
@click.argument('output_dir')
def fhir2transmart(input, output_dir):
    Console.title('FHIR to TranSMART')
    try:
        Console.info('Writing files to {}'.format(output_dir))
        writer = TransmartCopyWriter(output_dir)
        if path.isdir(input):
            filenames = [path.join(input, filename) for filename in os.listdir(input) if filename.endswith('.json')]
        else:
            filenames = [input]
        for filename in filenames:
            Console.info('Reading JSON from {}'.format(filename))
            with open(filename, 'r') as input_file:
                data = json.load(input_file)
                collection = FhirReader.read(data)
                result = Mapper.map(collection)
                writer.write_collection(result)
        Console.info('Done.')
    except LoaderException as e:
        Console.error(e)
        sys.exit(1)


if __name__ == '__main__':
    fhir2transmart()
