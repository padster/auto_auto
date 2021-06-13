# Load car options from Canada Drives


class CanadaDrivesSource:
    def path(self, opt):
        return (
            "https://shop.canadadrives.ca/cars/bc?SID2=buy-a-car-online-vancouver&" + \
            "region=BC&sort_by=product_price_asc&year={min_year}&transmission=automatic&product_price=0_{max_price}"
        ).format(**opt)
