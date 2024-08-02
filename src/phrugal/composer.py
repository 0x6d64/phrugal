class PhrugalComposer:
    def __init__(self, input_files):
        pass

    def create_compositions(self, images_count: int):
        """Does the following:

        - read the image metadata of the input files
        - figure out the images that go together in a single composition
        - for each composition: create it, and write the output into the output folder
        - after that, free the space of that composition

        - For each picture in the input, calculate the aspect ratio
            - if the aspect ratio is >1, calculate 1/aspect ratio (to normalize it)
        - sort the images by aspect ratio
        - do groups for N images
        - for each of the groups:
            - do all combinations of orders of images
            - for each combination: create score for the fit
                - todo: how can we assess the fit as a score?
            - then: select best, trigger actual creation of the image
        

        """
        pass
