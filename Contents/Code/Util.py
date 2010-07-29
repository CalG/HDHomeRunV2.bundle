
########################################
def XPathSelectOne(doc, query):
    nodes = doc.xpath(query)
    if len(nodes):
        node = nodes[0]
        try: text = node.text
        except AttributeError:
            text = str(node)
        return text
    else:
        return None
