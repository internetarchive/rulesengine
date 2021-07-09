

function getSurtNavChangeHandler(surtNavEl) {
  // Collect the ordered <select> elements.
  const selectEls = Array.from(surtNavEl.children)

  surtNavEl.addEventListener("change", e => {
    const el = e.target
    let partIdx = parseInt(el.name.split('-')[1])
    if (el.value === "__TRUNCATE__") {
      partIdx -= 1
    }
    // Clear search string altogether if truncate was selected in
    // the first (i.e. protocol) field.
    if (partIdx === -1) {
      window.location.search = ''
      return
    }
    // Generate a new surt up to the selected part index.
    let surt = (
      selectEls[0].value
      + "://("
      + selectEls.slice(1, partIdx + 1)
                  .map(el => el.value)
                  .join(',')
    )
    window.location.search = "?q=" + surt
  })
}

document.addEventListener("DOMContentLoaded", () => {
  const surtNavEl = document.getElementById("surt-part-navigator")
  surtNavEl.addEventListener("change", getSurtNavChangeHandler(surtNavEl))
})
