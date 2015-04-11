for (new_link in inc_links) {
    if (new_link in ctx._source.in_links) 
    {ctx._source.in_links = ctx._source.in_links} else {ctx._source.in_links = ctx._source.in_links + new_link}
}
