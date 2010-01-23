#!/bin/zsh

# Should be run from the docs directory: (cd docs && ./build-github.zsh)

REPO=$(dirname $(pwd))
GH=_gh-pages

# Update our local gh-pages branch
git checkout gh-pages && git pull && git checkout -


# Checkout the gh-pages branch, if necessary.
if [[ ! -d $GH ]]; then
    git clone $REPO $GH
    cd $GH
    git checkout -b gh-pages origin/gh-pages
    cd ..
fi

# Update the _gh-pages target dir.
cd $GH && git pull && cd ..

# Make a clean build.
make clean dirhtml

# Move the fresh build over.
cp -r _build/dirhtml/* $GH
cd $GH

# Commit.
git add .
git commit -am "gh-pages build on $(date)"
git push origin gh-pages
