
(function () {

  /*
     SURT Navigation
   */

  function getSurtNavChangeHandler(surtNavEl) {
    // Collect the ordered <select> elements.
    const selectEls = Array.from(surtNavEl.children)

    surtNavEl.addEventListener("change", e => {
      const el = e.target
      let partIdx = parseInt(el.name.split('-')[1])
      if (el.value === "") {
        partIdx -= 1
      }
      // Clear search string altogether if truncate was selected in
      // the first (i.e. protocol) field.
      if (partIdx === -1) {
        window.location.search = ''
        return
      }
      // Generate a new surt up to the selected part index.
      const encodedParams = []
      const protocol = selectEls[0].value
      if (protocol.length) {
        encodedParams.push(encodeURIComponent(`protocol = "${protocol}"`))
      }
      const surtPrefix = selectEls.slice(1, partIdx + 1)
                            .map(el => el.value)
                            .join(',')
      if (surtPrefix.length) {
        encodedParams.push(encodeURIComponent(`surt_prefix = "${surtPrefix}"`))
      }
      const joinedParams = encodedParams.join(" and ")
      window.location.search = joinedParams.length  ? `?q=${joinedParams}` : ''
    })
  }

  function initSurtNav () {
    const surtNavEl = document.getElementById("surt-part-navigator")
    surtNavEl.addEventListener("change", getSurtNavChangeHandler(surtNavEl))
  }

  /*
     Init
   */

  document.addEventListener("DOMContentLoaded", () => {
    initSurtNav()
  })

})()
