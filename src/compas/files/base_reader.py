from __future__ import absolute_import
from __future__ import division

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib2 import urlretrieve


class BaseReader(object):
    """Base class containing file reading functions for file extension specific readers

    Attributes
    ----------
    location : str or pathlib object
        Path or URL to the file
    is_url

    Methods
    -------
    location
    is_url
    is_binary
    is_valid
        Defined in subclasses
    download
        Download file specified by URL to temporary storage
    open_ascii
        Open ascii file specified by file path
    open_binary
        Open binary file specified by file path
    iter_lines
        Yields line from ascii file
    iter_chunks
        Yields chunks from binary file
    read
        Defined in subclasses
    check_file_signature
        Verify file signatures for file formats with file signature in format
        specification

    """
    def __init__(self, location):
        self._location = location
        self._is_url = None
        self._is_binary = None


    @property
    def location(self):
        """ Create or ensure Pathlib object for file

        Parameters
        ----------
        location : string or Pathlib object
            location specified either as an URL, string containing path or
            Pathlib object

        Raises
        ------
        IOError
            If file is not found
        """
        if self.is_url:
            pathobj = self.download(self._location)
        else:
            if not isinstance(self._location, Path):
                pathobj = Path(self._location)
            else:
                pathobj = self._location

        if pathobj.exists():
            return pathobj

        raise IOError('File not found.')

    @property
    def is_url(self):
        """Checks if given location is a string containing an URL

        Returns
        -------
        bool
            True if recognized as an URL
        """
        self._is_url = str(self._location).startswith('http')
        return self._is_url

    @property
    def is_binary(self):
        pass

    @property
    def is_valid(self):
        return NotImplementedError

    def download(self, url):
        """Downloads file and returns path to tempfle

        Called by property self.location

        Parameters
        ----------
        url : string
            URL to file

        Returns
        -------
        location : Pathlib object
            Path to tempfile
        """

        location, _ = urlretrieve(url)

        return Path(location)

    def open_ascii(self):
        """Open ascii or binary file and return file object

        Returns
        -------
        file object
        """
        try:
            file_object = self.location.open(mode='r')
        # unnecessary now?
        except UnicodeDecodeError:
            file_object = self.location.open(mode='r', errors='replace', newline='\r')
        return file_object

    def open_binary(self):
        """Open binary file and return file object

        Returns
        -------
        file object
        """

        return self.location.open(mode='rb')

    def iter_lines(self):
        """Yields lines from local ascii files

        Yields
        -------
        string
            Next line or chunk of file
        """
        # TODO: Handle continuing lines (as in OFF files)

        with self.open_ascii() as fo:
            for line in fo:
                yield line

    def iter_chunks(self, chunk_size=1024):
        """Yields lines from local binary files

        Parameters
        ----------
        chunk_size : int
            Chunks to read with each call

        Yields
        ------
        bytes
            Next chunk of file
        """
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError

    def check_file_signature(self):
        """Checks wether file signature (also known as magic number) is present
        in input file.

        File signatures are strings, numbers or bytes defined in a file
        format's specification. While not technically required to parse the
        file, a missing file signatures might be a sign of a malformed file.

        More information about file signatures can be found on Wikipedia[1]_
        as well as examples of file signatures[2]_

        Raises
        ------
        Exception
            If file signature is specified for file format but not present
            in file.

        .. [1] https://en.wikipedia.org/wiki/List_of_file_signatures
        .. [2] https://en.wikipedia.org/wiki/File_format#Magic_number
        """
        # TODO: Integrate with is_binary checks in file readers
        # TODO. Look into binaryornot library to help with above

        try:
            file_signature = self.FILE_SIGNATURE['content']
            signature_offset = self.FILE_SIGNATURE['offset']

        # if file type has no associated file signature
        except AttributeError:
            return

        with self.location.open(mode="rb") as fd:
            fd.seek(signature_offset)
            found_signature = fd.read(len(file_signature))

        if isinstance(found_signature, str) and found_signature != file_signature.decode():
            raise Exception('File not valid, import failed.')
        elif found_signature != file_signature:
            raise Exception('File not valid, import failed.')
