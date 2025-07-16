import re
import pandas as pd
from langchain.docstore.document import Document

def extract_references(text):
    reference_patterns = [
        r'(see|refer to|as shown in)\s+table\s+(\d+\.\d+|\d+)',
        r'(see|refer to|as shown in)\s+figure\s+(\d+\.\d+|\d+)',
        r'(see|refer to|as shown in)\s+section\s+(\d+\.\d+|\d+)',
        r'(see|refer to|as shown in)\s+appendix\s+([a-zA-Z])'
    ]
    
    references = []
    for pattern in reference_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            ref_type = match.group(1)
            ref_id = match.group(2)
            references.append({
                'type': ref_type.lower(),
                'id': ref_id,
                'full_match': match.group(0)
            })
    
    return references

def index_document_sections(documents):
    section_index = {}
    table_index = {}
    figure_index = {}
    
    section_pattern = r'^(\d+\.\d+|\d+)\s+([A-Za-z][\w\s]+)'
    table_pattern = r'Table\s+(\d+\.\d+|\d+)[:\s]+([A-Za-z][\w\s]+)'
    figure_pattern = r'Figure\s+(\d+\.\d+|\d+)[:\s]+([A-Za-z][\w\s]+)'
    
    for i, doc in enumerate(documents):
        text = doc.page_content
        
        # Index sections
        section_matches = re.finditer(section_pattern, text, re.MULTILINE)
        for match in section_matches:
            section_id = match.group(1)
            section_title = match.group(2).strip()
            section_index[section_id] = {
                'title': section_title,
                'doc_id': i,
                'start_idx': match.start()
            }
        
        # Index tables
        table_matches = re.finditer(table_pattern, text, re.MULTILINE)
        for match in table_matches:
            table_id = match.group(1)
            table_title = match.group(2).strip()
            table_index[table_id] = {
                'title': table_title,
                'doc_id': i,
                'start_idx': match.start()
            }
        
        # Index figures
        figure_matches = re.finditer(figure_pattern, text, re.MULTILINE)
        for match in figure_matches:
            figure_id = match.group(1)
            figure_title = match.group(2).strip()
            figure_index[figure_id] = {
                'title': figure_title,
                'doc_id': i,
                'start_idx': match.start()
            }
    
    return {
        'sections': section_index,
        'tables': table_index,
        'figures': figure_index
    }

def resolve_cross_references(documents):
    # Extract all references
    all_references = []
    for i, doc in enumerate(documents):
        references = extract_references(doc.page_content)
        for ref in references:
            ref['doc_id'] = i
            all_references.append(ref)
    
    # Index document sections, tables, and figures
    index = index_document_sections(documents)
    
    # Add metadata to documents
    for doc in documents:
        doc.metadata['references'] = []
    
    # Resolve references
    for ref in all_references:
        doc_id = ref['doc_id']
        ref_id = ref['id']
        
        if 'table' in ref['full_match'].lower() and ref_id in index['tables']:
            target = index['tables'][ref_id]
            documents[doc_id].metadata['references'].append({
                'type': 'table',
                'id': ref_id,
                'title': target['title'],
                'target_doc_id': target['doc_id']
            })
        
        elif 'figure' in ref['full_match'].lower() and ref_id in index['figures']:
            target = index['figures'][ref_id]
            documents[doc_id].metadata['references'].append({
                'type': 'figure',
                'id': ref_id,
                'title': target['title'],
                'target_doc_id': target['doc_id']
            })
        
        elif 'section' in ref['full_match'].lower() and ref_id in index['sections']:
            target = index['sections'][ref_id]
            documents[doc_id].metadata['references'].append({
                'type': 'section',
                'id': ref_id,
                'title': target['title'],
                'target_doc_id': target['doc_id']
            })
    
    return documents

def enhance_retrieval_with_references(query_results, all_documents, max_references=2):
    enhanced_results = list(query_results)
    references_added = 0
    
    for doc in query_results:
        if 'references' in doc.metadata and references_added < max_references:
            for ref in doc.metadata['references']:
                target_doc_id = ref.get('target_doc_id')
                if target_doc_id is not None and target_doc_id < len(all_documents):
                    referenced_doc = all_documents[target_doc_id]
                    if referenced_doc not in enhanced_results:
                        enhanced_results.append(referenced_doc)
                        references_added += 1
                        if references_added >= max_references:
                            break
    
    return enhanced_results 