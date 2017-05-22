

def delete_file(vendor, path, ignore_prefix=False):
    from wanna import setup_vendor

    vendor = setup_vendor(vendor, ignore_prefix=ignore_prefix)
    vendor.delete_file(path)


def list_files(vendor, ignore_prefix=False):
    from wanna import setup_vendor

    vendor = setup_vendor(vendor, ignore_prefix=ignore_prefix)
    vendor.list_files()
