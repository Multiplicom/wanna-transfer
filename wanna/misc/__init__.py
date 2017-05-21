

def delete_file(vendor, ignore_prefix=False):
    pass


def list_files(vendor, ignore_prefix=False):
    from wanna import setup_vendor

    vendor = setup_vendor(vendor)
    vendor.list_files()
