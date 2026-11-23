=========
CHANGELOG
=========

Notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__.

Unreleased
----------

* Added the ``swxsoc_reach.calibration.legacy`` module to process Aerospace "Legacy" pipeline daily per-spacecraft CSVs (``reach.YYYYMMDD.vid-NNN.l1b.v3.csv``) into two daily 5-second CDFs: an L1 file (``reach_all_l1_5s_YYYYMMDD``) with dose rates, housekeeping monitors, and ``lm``, and an L2 file (``reach_all_l2_5s_YYYYMMDD``) with magnetic coordinates, region/orbit codes, and proton/electron flux and species. The entry point :func:`~swxsoc_reach.calibration.legacy.process_legacy_day` returns a list of output file paths.
* Added Legacy CSV readers (``read_legacy_csv``, ``read_legacy_pipeline_files``, ``read_legacy_pipeline_day``) to ``swxsoc_reach.io.file_tools``, ``parse_legacy_pipeline_filename`` to ``swxsoc_reach.util.util``, and the ``dosimeter_flavor`` lookup to ``swxsoc_reach.util.enums``.
* Changed ``create_reach_filename`` to use a date-only timestamp (``YYYYMMDD``) for L1 files and ``5s`` daily files.
* Changed the ``Logical_source`` global attribute to include the data level (e.g. ``reach_all_l1c_prelim``, ``reach_all_l1_5s``), and ``Logical_source``/``Logical_file_id`` are now always derived from the current metadata.
* Replaced the ``UDL_Source`` global attribute with ``Source_pipeline`` (``UDL_PROVISIONAL``, ``UDL_QUICKLOOK``, or ``LEGACY_PIPELINE``) and added a ``Parents`` global attribute listing the source file names.
* Updated the UDL-to-CDF transform: delivered FILLVAL entries are converted to NaN before building arrays, ``sensor_ids``/``dosimeter_flavor_ids`` are stored as ``uint8``, ``obQuality`` is stored as masked ``int8`` with flag descriptions, ``dose_rate`` units are corrected to rad/s with valid ranges and log scaling, and ``lat``/``lon``/``alt`` are described as geodetic with valid ranges. ``create_sensor_array`` and ``create_observation_array`` accept a column name and dtype, and a ``masked_int8_ndata`` helper was added.
* Added Legacy test fixtures (CSV plus L1/L2 CDFs) and tests for the Legacy pipeline, regenerated the UDL L1C test CDF, and added tests that check the committed test CDFs agree with processing their source CSVs (global attributes, variables, types, shapes, and variable attributes).
* Added ``REACHTrack`` addition for combining compatible tracks, including support and spectra data concatenation, duplicate-entry removal with logging, regression tests, and user-guide documentation.
* Added :class:`~swxsoc_reach.track.trackbase.REACHTrack`, a container for L1C dosimeter track data.
* Added :class:`~swxsoc_reach.geomap.geomapbase.GenericGeoMap`, a SunPy-like gridded geospatial map container with per-statistic/per-flavor data access.
* Added the :class:`~swxsoc_reach.util.enums.Flavor`, :class:`~swxsoc_reach.util.enums.SensorId`, and :class:`~swxsoc_reach.util.enums.Region` enumerations.
* Added the ``swxsoc_reach.util.geom`` module of region-geometry utilities to build, save, and load region contour paths.
* Added geomap plotting helpers to ``swxsoc_reach.visualization.viz`` using canonical ``Region`` colors and contour levels.
* Added the ``load_regions`` helper to ``swxsoc_reach.util.util`` to expose region longitudes, latitudes, and codes from the bundled contour data.
* Extended the processing pipeline so ``process_file`` converts L1C/CDF input into a combined geomap CDF plus per-flavor, per-statistic PNG plots.
* Added user guide pages for the constellation and enums (``constellation.rst``), region geometry (``geom.rst``), and the new map and track data objects (``data_objects.rst``).
* Added test coverage for the flavor/enum, geometry, geomap, track, and visualization modules.
* Project foundation and scaffolding were established, including the initial repository setup and template alignment.
* Update to support data pipeline, imports JSON files from UDL and outputs to CDF with ISTP-compliant metadata.
* Runtime and reliability improvements included temporary-path handling, logging improvements, and threaded UDL download support.
* Developer experience was improved through dependency updates, NumPy/doctest constraint refinements, formatting/test updates, and devcontainer/workflow maintenance.
* Documentation and release-readiness work expanded substantially, including docstring updates, Read the Docs/DOI integration, and new customization/changelog documentation.
* Updated docs build behavior to run Sphinx via the active Python environment (``python -m sphinx``) to avoid Homebrew executable conflicts.
* Fixed README badge definitions and URLs (GitHub Actions org links and coverage badge reStructuredText syntax).
* Added package version display to the About page using the Sphinx ``|release|`` substitution.
* Improved changelog discoverability from the docs landing page with a direct link.
