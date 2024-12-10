import os

import pymupdf
import numpy as np

from lezgi_text.utils import (
    canonize_lez,
    fix_cp1252_encoding,
    tv_guide_classifier_regex,
    is_lezgian,
    is_trash,
    is_poem,
    remove_hyphens,
    remove_double_spaces,
    remove_url,
    remove_email_addresses,
    remove_nonprintable_chars,
    remove_emojis,
    casing_errors_fix
)


_pymupdf_active_flags = [
    pymupdf.TEXT_DEHYPHENATE,
    pymupdf.TEXT_INHIBIT_SPACES,
    pymupdf.TEXT_PRESERVE_LIGATURES,
    pymupdf.TEXT_PRESERVE_WHITESPACE,
    pymupdf.TEXT_MEDIABOX_CLIP,
    pymupdf.TEXT_CID_FOR_UNKNOWN_UNICODE
]

_pymupdf_inactive_flags = [
    ~pymupdf.TEXT_PRESERVE_IMAGES,
]

_pymupdf_flags = np.bitwise_or.reduce(_pymupdf_active_flags).item() & \
                    np.bitwise_and.reduce(_pymupdf_inactive_flags).item()


def parse_lezgi_gazet(
    pdf_path: str | os.PathLike,
) -> tuple[list[str], list[str], list[str]]:
    global _pymupdf_flags

    accepted_paragraphs = list()
    rejected_paragraphs = list()
    rejection_reasons = list()

    doc = pymupdf.open(pdf_path)

    for i, page in enumerate(doc):
        page_text = page.get_text('text')
        page_text = fix_cp1252_encoding(page_text)
    
        if tv_guide_classifier_regex(page_text):
            rejected_paragraphs.append(page_text)
            rejection_reasons.append('tv guide')
            continue
    
        page_dict = page.get_text(
            option='dict',
            sort=False,
            flags=_pymupdf_flags
        )
    
        paragraphs = list()
        p = ''
        prev_size = None
    
        for block in page_dict['blocks']:
            for line in block['lines']:
                for span in line['spans']:
                    cur_size = span['size']
                    t = remove_nonprintable_chars(span['text'])
                    if prev_size and cur_size != prev_size:
                        paragraphs.append(p)
                        p = ""
                    prev_size = cur_size
    
                    if t.strip() not in ['-', '']:
                        p += t + '\n'
            
        if p:
            paragraphs.append(p)

        paragraphs = map(fix_cp1252_encoding, paragraphs)
        paragraphs = map(canonize_lez, paragraphs)
        paragraphs = map(remove_hyphens, paragraphs)
        paragraphs = [' '.join(p.splitlines()) for p in paragraphs]
        paragraphs = map(remove_double_spaces, paragraphs)
        paragraphs = map(remove_url, paragraphs)
        paragraphs = map(remove_email_addresses, paragraphs)
        paragraphs = map(remove_emojis, paragraphs)
        paragraphs = map(casing_errors_fix, paragraphs)

        for p in paragraphs:
            if is_trash(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('trash')
                continue
            if not is_lezgian(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('language')
                continue

            accepted_paragraphs.append(p)
        
    return accepted_paragraphs, rejected_paragraphs, rejection_reasons


def parse_tsiyi_dunya(
    pdf_path: str | os.PathLike,
) -> tuple[list[str], list[str], list[str]]:
    global _pymupdf_flags

    accepted_paragraphs = list()
    rejected_paragraphs = list()
    rejection_reasons = list()

    doc = pymupdf.open(pdf_path)

    for i, page in enumerate(doc):
        page_text = page.get_text('text')
        page_text = fix_cp1252_encoding(page_text)
    
        if tv_guide_classifier_regex(page_text):
            rejected_paragraphs.append(page_text)
            rejection_reasons.append('tv guide')
            continue
    
        page_dict = page.get_text(
            option='dict',
            sort=False,
            flags=_pymupdf_flags
        )
    
        paragraphs = list()
        p = ''
        prev_font = ''
    
        for block in page_dict['blocks']:
            for line in block['lines']:
                for span in line['spans']:
                    cur_font = span['font'] + str(span['size'])
                    t = remove_nonprintable_chars(span['text'])
                    if (
                        (prev_font and cur_font != prev_font)
                    ):
                        paragraphs.append(p)
                        p = ""

                    prev_font = cur_font
    
                    if t.strip() not in ['-', '']:
                        if t.strip()[0].isupper():
                            p += ' ' + t # + '\n'
                        else:
                            p += t

                    if (len(t) <= 2 and t.istitle()):
                        prev_font = ''
            
        if p:
            paragraphs.append(p)

        paragraphs = map(str.strip, paragraphs)
        paragraphs = map(fix_cp1252_encoding, paragraphs)
        paragraphs = map(canonize_lez, paragraphs)
        paragraphs = map(remove_hyphens, paragraphs)
        paragraphs = [' '.join(p.splitlines()) for p in paragraphs]
        paragraphs = map(remove_nonprintable_chars, paragraphs)
        paragraphs = map(remove_double_spaces, paragraphs)
        paragraphs = map(remove_url, paragraphs)
        paragraphs = map(remove_email_addresses, paragraphs)
        paragraphs = map(remove_emojis, paragraphs)
        paragraphs = map(casing_errors_fix, paragraphs)

        for p in paragraphs:
            if is_trash(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('trash')
                continue
            if not is_lezgian(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('language')
                continue

            accepted_paragraphs.append(p)
        
    return accepted_paragraphs, rejected_paragraphs, rejection_reasons


def parse_lit_dag(
    pdf_path: str | os.PathLike,
) -> tuple[list[str], list[str], list[str]]:
    global _pymupdf_flags

    accepted_paragraphs = list()
    rejected_paragraphs = list()
    rejection_reasons = list()

    doc = pymupdf.open(pdf_path)

    for i, page in enumerate(doc):
        page_text = page.get_text('text')
        page_text = fix_cp1252_encoding(page_text)
    
        if tv_guide_classifier_regex(page_text):
            rejected_paragraphs.append(page_text)
            rejection_reasons.append('tv guide')
            continue

        if is_poem(page_text):
            rejected_paragraphs.append(page_text)
            rejection_reasons.append('poem')
            continue
    
        page_dict = page.get_text(
            option='dict',
            sort=False,
            flags=_pymupdf_flags
        )
    
        paragraphs = list()
        p = ''
        prev_font = ''
    
        for block in page_dict['blocks']:
            for line in block['lines']:
                for span in line['spans']:
                    cur_font = span['font'] + str(span['size'])
                    t = remove_nonprintable_chars(span['text'])
                    if (
                        (prev_font and cur_font != prev_font)
                    ):
                        paragraphs.append(p)
                        p = ""

                    prev_font = cur_font
    
                    if t.strip() not in ['-', '']:
                        if t.strip()[0].isupper():
                            p += ' ' + t # + '\n'
                        else:
                            p += t

                    if (len(t) <= 2 and t.istitle()):
                        prev_font = ''
            
        if p:
            paragraphs.append(p)

        paragraphs = map(str.strip, paragraphs)
        paragraphs = map(fix_cp1252_encoding, paragraphs)
        paragraphs = map(canonize_lez, paragraphs)
        paragraphs = map(remove_hyphens, paragraphs)
        paragraphs = [' '.join(p.splitlines()) for p in paragraphs]
        paragraphs = map(remove_nonprintable_chars, paragraphs)
        paragraphs = map(remove_double_spaces, paragraphs)
        paragraphs = map(remove_url, paragraphs)
        paragraphs = map(remove_email_addresses, paragraphs)
        paragraphs = map(remove_emojis, paragraphs)
        paragraphs = map(casing_errors_fix, paragraphs)

        for p in paragraphs:
            if is_trash(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('trash')
                continue
            if not is_lezgian(p):
                rejected_paragraphs.append(p)
                rejection_reasons.append('language')
                continue

            accepted_paragraphs.append(p)
        
    return accepted_paragraphs, rejected_paragraphs, rejection_reasons


def parse_erenlardin_ses(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_lezgi_gazet(pdf_path)


def parse_dagdin_bulah(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_lezgi_gazet(pdf_path)


def parse_cure_habar(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_lezgi_gazet(pdf_path)


def parse_samurdin_ses(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_lezgi_gazet(pdf_path)


def parse_samur(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_lezgi_gazet(pdf_path)


def parse_alam(pdf_path: str | os.PathLike) -> tuple[list[str], list[str], list[str]]:
    return parse_tsiyi_dunya(pdf_path)
