-- Samakan sitasi DOCX dengan keluaran biblatex-apa pada template ta-sti.
-- biblatex menulis "(Chen dkk. 2025)", citeproc menulis "(Chen dkk., 2025)".
-- Template tidak menerjemahkan "nodate", jadi PDF menulis "n.d.", citeproc id-ID menulis "t.t.".
-- Filter ini dipasang SESUDAH --citeproc pada perintah pandoc.
function Cite(el)
  el.content = el.content:walk({
    Str = function(s)
      if s.text:match("dkk%.,$") then
        s.text = s.text:gsub("dkk%.,$", "dkk.")
      end
      s.text = s.text:gsub("t%.t%.", "n.d.")
      return s
    end
  })
  return el
end
