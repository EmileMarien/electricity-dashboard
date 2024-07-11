

from context import SLP_xls_to_pd, SPP_xls_to_pd


print(SLP_xls_to_pd(file_path='data/slp_enu_cons.xls').to_dict())
# check type of index
#print(SLP_xls_to_pd(file_path='data/slp_enu_cons.xls').index.dtype)
#print(SPP_xls_to_pd(file_path='data/SPP_2022_(Ex-ante_and_Ex-post)_v1_0_prod.xlsx'))

