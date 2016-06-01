#!/usr/bin/python

import os
import tempfile

from Datatype import Datatype
from Track import Track
from TrackDb import TrackDb
from util import subtools


class BedSimpleRepeats( Datatype ):
    def __init__( self, input_bed_simple_repeats_false_path, data_bed_simple_repeats,
                 input_fasta_file, extra_files_path, tool_directory ):

        super(BedSimpleRepeats, self).__init__(
                input_fasta_file, extra_files_path, tool_directory
        )

        self.input_bed_simple_repeats_false_path = input_bed_simple_repeats_false_path
        self.name_bed_simple_repeats = data_bed_simple_repeats["name"]

        sortedBedFile = tempfile.NamedTemporaryFile(suffix=".sortedBed")
        twoBitInfoFile = tempfile.NamedTemporaryFile(bufsize=0)
        chromSizesFile = tempfile.NamedTemporaryFile(bufsize=0, suffix=".chrom.sizes")

        # Sort processing
        subtools.sort(self.input_bed_simple_repeats_false_path, sortedBedFile.name)

        # TODO: Regroup in an mother class which handles the Chrom.sizes creation with Gff3 and Gtf
        # Generate the chrom.sizes

        subtools.twoBitInfo(self.twoBitFile.name, twoBitInfoFile.name)

        # Then we get the output to inject into the sort
        # TODO: Check if no errors
        subtools.sortChromSizes(twoBitInfoFile.name, chromSizesFile.name)

        # bedToBigBed processing
        # TODO: Change the name of the bb, to tool + genome + .bb
        trackName = "".join( ( self.name_bed_simple_repeats, '.bb' ) )
        myBigBedFilePath = os.path.join(self.myTrackFolderPath, trackName)
        auto_sql_option = "%s%s" % ('-as=', os.path.join(self.tool_directory, 'trf_simpleRepeat.as'))
        with open(myBigBedFilePath, 'w') as bigBedFile:
            subtools.bedToBigBed(sortedBedFile.name, chromSizesFile.name, bigBedFile.name,
                                 typeOption='-type=bed4+12',
                                 autoSql=auto_sql_option)

        # Create the Track Object
        dataURL = "tracks/%s" % trackName

        trackDb = TrackDb(
            trackName=trackName,
            longLabel='Tandem Repeats Big by TrfBig',
            shortLabel='Tandem Repeats',
            trackDataURL=dataURL,
            trackType='bigBed 4 +',
            visibility='dense'
        )

        self.track = Track(
            trackFile=myBigBedFilePath,
            trackDb=trackDb,
        )

        print("- %s created in %s" % (trackName, myBigBedFilePath))
