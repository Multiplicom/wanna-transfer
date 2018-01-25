
def setup_vendor(vendor, **kwargs):
    from wanna import setup_vendor
    return setup_vendor(vendor, **kwargs)


def delete_file(vendor, path, **kwargs):
    vendor = setup_vendor(vendor, **kwargs)
    return vendor.delete_file(path)


def search_files(vendor, term, **kwargs):
    vendor = setup_vendor(vendor, **kwargs)
    return vendor.search(term)


def rename_file(vendor, old, new, **kwargs):
    vendor = setup_vendor(vendor, **kwargs)
    return vendor.rename_object(old, new)


def list_files(vendor, **kwargs):
    vendor = setup_vendor(vendor, **kwargs)
    return vendor.list_files()


def get_status(vendor, path, **kwargs):
    vendor = setup_vendor(vendor, **kwargs)
    return vendor.get_status(path)
