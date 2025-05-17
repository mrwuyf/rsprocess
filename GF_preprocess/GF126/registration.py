import arosics
from geoarray import GeoArray

ref_image = r"E:\dataset\bridge\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001_有问题\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001-PAN2_ortho.tiff"
tgt_image = r'E:\dataset\bridge\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001_有问题\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001-MSS2_ortho.tiff'

coreg = arosics.COREG(
    im_ref=ref_image,
    im_tgt=tgt_image,
    path_out=r'E:\dataset\bridge\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001_有问题\GF2_PMS2_E109.8_N34.5_20240517_L1A13847895001-MSS2_registration.tiff',
    fmt_out='GTIFF',
    max_shift=20)
coreg.calculate_spatial_shifts()
coreg.correct_shifts()