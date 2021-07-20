
(function () {

  /*
     Helpers
   */

  function calcRenderedTextWidthPx (text) {
    const container = document.createElement("span")
    container.textContent = text
    container.style.display = "inline-block"
    container.style.visibility = "hidden"
    document.body.appendChild(container)
    const width = parseFloat(window.getComputedStyle(container).width)
    container.remove()
    return width
  }

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
     Column Resize Handles
   */

  function initColumnResizeHandles (tableEl) {
    // Define some state.
    const state = { activeHandle: null, lastX: null }

    // Get the first table > thead > tr element.
    const tableRowEl = tableEl.querySelector('thead > tr')

    tableRowEl.addEventListener("dblclick", e => {
      // When a resize handle element is double-clicked, toggle its <th>
      // parent width between minWidth/maxWidth.
      if (!e.target.classList.contains("resize-handle")) {
        return
      }
      e.stopPropagation()
      e.preventDefault()
      const thEl = e.target.parentNode
      thEl.style.width =
        (parseFloat(thEl.style.width) < parseFloat(thEl.style.maxWidth))
        ? thEl.style.maxWidth
        : thEl.style.minWidth
    })

    tableRowEl.addEventListener("mousedown", e => {
      // When a resize handle element is moused-down, save the element to state
      // and save the current mouse x position.
      if (!e.target.classList.contains("resize-handle")) {
        return
      }
      e.stopPropagation()
      e.preventDefault()
      state.activeHandle = e.target
      state.lastX = e.clientX
    })

    document.addEventListener("mousemove", e => {
      // When the mouse is moved when a resize handle is active, adjust the
      // width of the resize handle's parent <th> element along with the
      // change in the mouse x-axis position.
      if (state.activeHandle === null) {
        return
      }
      e.stopPropagation()
      e.preventDefault()
      const thEl = state.activeHandle.parentNode
      const delta = e.clientX - state.lastX
      // Clamp to min/max because Chrome doesn't respect the CSS values for
      // table cells.
      const widthPx = Math.max(
        Math.min(
          parseFloat(thEl.style.width) + delta,
          parseFloat(thEl.style.maxWidth)
        ),
        parseFloat(thEl.style.minWidth)
      )
      thEl.style.width = `${widthPx}px`
      state.lastX = e.clientX
    })

    document.addEventListener("mouseup", e => {
      // Clear state.activeHandle on mouse up.
      if (state.activeHandle === null) {
        return
      }
      e.stopPropagation()
      e.preventDefault()
      state.activeHandle = null
    })

    // Define a resize handle element that we'll clone for each cell.
    const handleEl = document.createElement("span")
    handleEl.classList.add("resize-handle")
    handleEl.style.position = "absolute"
    handleEl.style.display = "inline-block"
    handleEl.style.width = "0.4em"
    handleEl.style.height = "100%"
    handleEl.style.right = "0"
    handleEl.style.backgroundColor = "#ddd"
    handleEl.style.cursor = "col-resize"

    Array.from(tableRowEl.children).forEach((thEl, i) => {
      // Pre-calculate the width of the longest content in this column.
      const maxWidthPx = Array.from(
        tableEl.querySelectorAll(`tbody > tr > *:nth-child(${i+1})`)
      ).reduce(
        (acc, cellEl) =>
          Math.max(acc, calcRenderedTextWidthPx(cellEl.textContent)),
        0
      )

      // Calculate and set the width of each <th> element so that we can
      // recalculate mousemove deltas against this value.
      const thElComputedWidth = window.getComputedStyle(thEl).width
      thEl.style.minWidth = thElComputedWidth
      thEl.style.width = thElComputedWidth
      thEl.style.maxWidth =
        `${Math.max(maxWidthPx, parseFloat(thElComputedWidth))}px`
      // Only add a resize handle element if the column is currently smaller
      // than its max width.
      if (thEl.style.minWidth !== thEl.style.maxWidth) {
        thEl.insertBefore(handleEl.cloneNode(), thEl.children[0])
      }
    })

    // Set table-layout=fixed (after having manually set the computed width of
    // each <th>) to make the resizing work.
    tableEl.style.tableLayout = "fixed"
  }


  /*
     Init
   */

  document.addEventListener("DOMContentLoaded", () => {
    initSurtNav()
    initColumnResizeHandles(document.querySelector("#result_list"))
  })

})()
