Configuration
=============

Creating a default config
-------------------------
Run the tool with the parameter ``--create-default-config``. The parameter accepts an optional
path to the template file.

Available decoration items
--------------------------

.. csv-table::
   :file: ./config-params.csv
   :widths: 30, 100, 200
   :header-rows: 1
   :class: longtable

Limitations of geocoding
^^^^^^^^^^^^^^^^^^^^^^^^

Zoom levels
"""""""""""

As a backend for geocoding we use `Nominatim <https://nominatim.org/>`_.
The zoom level that is configured controls how many details are fetched from the server.
Nominatim uses the following levels (`source <https://nominatim.org/release-docs/latest/api/Reverse/#result-restriction>`_):

 ====== =========================
  zoom   address detail
 ====== =========================
  3      country
  5      state
  8      county
  10     city
  12     town / borough
  13     village / suburb
  14     neighbourhood
  15     any settlement
  16     major streets
  17     major and minor streets
  18     building
 ====== =========================

In phrugal, we simplify the output and *do not** output all of the listed elements.
Phrugal limits the output to the following parts:

* country
* state
* county
* city
* road

*Rationale:* for locations in Romania and Germany the information that is returned by
the OpenStreetMap database contains mappings of locations that are not connected
to the location names used by locals. Example: the location lat=49.802631, lon=9.950566
is a building in the quarter "Grombühl" of Würzburg (a town in Germany), and Nominatim
maps it to the "Dürrbachtal" neighborhood at zoom level 14. I'm not sure about the root
cause, but I decided for now to just omit the values that don't make sense.
Printing all the values is not desirable anyway, since this would make the string too long
to be usable.

As a potential improvement, future versions could make the list above configurable so that
the user can define what parts of an address shall be included in the output.

Geocoding speed
"""""""""""""""
Nominatim rate limits queries to 1 query per second. Phrugal implements a delay
that honors this requirement, so using geocoding is slow but should usually
work without any error.
