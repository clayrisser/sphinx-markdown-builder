function ready(cb) {
  if (
    document.attachEvent
      ? document.readyState === 'complete'
      : document.readyState !== 'loading'
  ) {
    cb();
  } else {
    document.addEventListener('DOMContentLoaded', cb);
  }
}
ready(function() {
  // put custom scripts here
});
