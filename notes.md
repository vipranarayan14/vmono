# Steps to add support for multiple files

1. change 'QFileDialog.getOpenFileName' to 'QFileDialog.getOpenFileNames' in on_open_btn_click
2. pass the tuple of `filenames` to load_img
3. rename load_img to load_images
4. make `self.data` dict.
5. in load_images: 
   1. for each `filepath` in `filepaths` tuple; 
      1. get only the `filename` from `filepath` and add it to `self.data.filenames`
      2. load image and add to array and convert array into tuple. add to `self.data.images` 
      3. create input previews tuple and add it `self.data.input_previews`
      4. create output previews array and add it to `self.data.output_previews`
6. 

# TODOS
- [x] Add support for opening multiple files
  - [x] array contains filenames
  - [x] next btn switches to next preview.
- [ ] Use threshold_display label as messagebox for showing
  - [ ] open instruction
  - [ ] threshold val
  - [ ] saved status and filepath
- [x] Update window title with opened filename
- [ ] Show stacked previews instead of side-by-side view
- [ ] Make `self.threshold_display` relative to content size or window size
- [x] Make previews resize on window resize
- [x] Use low-quality image for perviews
- [-] Support opening of any image format.
- [x] Fix previews and threshold display not updating when next or prev btns are clicked.
- [ ] Rearrange imports in alphabetical order.
- [ ] (Find a way to) Add ImageMagick to app bundle
