# Pixel Junction

Personal blog by [Peter van Beek](https://github.com/pvbnet), live at [pvbnet.github.io](https://pvbnet.github.io).

Built with [Jekyll](https://jekyllrb.com/) and the [Rain theme](https://github.com/inelaah/rain). The site is hosted on GitHub Pages — pushing to `master` publishes automatically.


## Writing and publishing posts

1. Create a file in `_posts/` named `YYYY-MM-DD-slug.md`. Include front matter with
`layout` and `title` fields at minimum (see existing posts for examples).
2. Put post images in `assets/posts/<post-slug>/`, not in `_posts/`.
3. Write your post in Markdown below the front matter.
4. Optional: preview with `bundle exec jekyll serve`.
5. Git commit and push to `master` — GitHub Pages rebuilds the site within a minute or two.


## Publishing a post to Medium

Medium cannot render LaTeX used for equations, so convert the article first, publish the converted page, then import that URL in Medium.

1. From `_scripts/`, convert the post: 

   ```bash
   cd _scripts
   source .venv/bin/activate
   python3 convert_equations.py ../_posts/YYYY-MM-DD-slug.md \
     --output ../medium/YYYY-MM-DD-slug.md \
     --outdir ../assets/posts/YYYY-MM-DD-slug/eqn
   ```

This adds images for equations into the existing assets folder structure while moving the converted Markdown file to the `medium/` folder. You can preview the converted page and make any necessary changes before publishing it.

2. Commit and push to `master`. The converted page is live at `https://pvbnet.github.io/medium/YYYY-MM-DD-slug.html`. Example: [https://pvbnet.github.io/medium/2026-08-01-nn-attention-and-nlm.html](https://pvbnet.github.io/medium/2026-08-01-nn-attention-and-nlm.html). Although published on github pages, it is not visible in the blog table of contents and not indexed by search engines.

3. In Medium, use **Import a story** and paste the URL `https://pvbnet.github.io/medium/YYYY-MM-DD-slug.html`. Medium handles the images properly. You can make final tweaks in the Medium editor.


## Local setup to preview posts

Requires Ruby 3.2 and [Bundler](https://bundler.io/).

```bash
sudo apt install ruby-full build-essential zlib1g-dev

gem install bundler --user-install
export PATH="$HOME/.local/share/gem/ruby/3.2.0/bin:$PATH"   # add to ~/.bashrc to persist

bundle config set --local path 'vendor/bundle'
bundle install
bundle exec jekyll serve
```

Open [http://localhost:4000](http://localhost:4000). The `github-pages` gem keeps the local build aligned with GitHub Pages.
