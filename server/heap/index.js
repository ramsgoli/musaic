const { heapId } = require('../config')

const addHeapTracking = (req, res, next) => {
  res.locals.heapId = heapId
  next()
}

module.exports = { addHeapTracking }
