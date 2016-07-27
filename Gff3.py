#!/usr/bin/python

import os
import tempfile

# Internal dependencies
from Datatype import Datatype
from Track import Track
from TrackDb import TrackDb
from util import subtools


class Gff3( Datatype ):
    def __init__(self, input_Gff3_false_path, data_gff3):
        super( Gff3, self ).__init__()

        self.track = None

        self.input_Gff3_false_path = input_Gff3_false_path
        self.name_gff3 = data_gff3["name"]
        self.priority = data_gff3["order_index"]

        # TODO: See if we need these temporary files as part of the generated files
        genePredFile = tempfile.NamedTemporaryFile(bufsize=0, suffix=".genePred")
        unsortedBedFile = tempfile.NamedTemporaryFile(bufsize=0, suffix=".unsortedBed")
        sortedBedFile = tempfile.NamedTemporaryFile(suffix=".sortedBed")

        # TODO: Refactor into another Class to manage the twoBitInfo and ChromSizes (same process as in Gtf.py)

        # gff3ToGenePred processing
        subtools.gff3ToGenePred(self.input_Gff3_false_path, genePredFile.name)

        # TODO: From there, refactor because common use with Gtf.py
        # genePredToBed processing
        subtools.genePredToBed(genePredFile.name, unsortedBedFile.name)

        # Sort processing
        subtools.sort(unsortedBedFile.name, sortedBedFile.name)

        # TODO: Check if no errors

        # bedToBigBed processing
        # TODO: Change the name of the bb, to tool + genome + possible adding if multiple +  .bb
        trackName = "".join( (self.name_gff3, ".bb" ) )
        myBigBedFilePath = os.path.join(self.myTrackFolderPath, trackName)
        with open(myBigBedFilePath, 'w') as bigBedFile:
            subtools.bedToBigBed(sortedBedFile.name, self.chromSizesFile.name, bigBedFile.name)

        # Create the Track Object
        dataURL = "tracks/%s" % trackName

        trackDb = TrackDb(
            trackName=trackName,
            longLabel=self.name_gff3,
            shortLabel=self.getShortName( self.name_gff3 ),
            trackDataURL=dataURL,
            trackType='bigBed 12 +',
            visibility='dense',
            priority=self.priority,
        )

        self.track = Track(
            trackFile=myBigBedFilePath,
            trackDb=trackDb,
        )

        #print("- %s created in %s" % (trackName, myBigBedFilePath))
