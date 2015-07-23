
tags=$(git ls-remote --tags https://github.com/bokeh/bokeh.git| awk '{print $2;}' | egrep '/([0-9.]+)$' | cut -d"/" -f3 | sort -r)
set -e
for tag in ${tags[@]}
do
    echo $tag
    pip --isolated install --quiet bokeh==$tag
    python -c 'from bokeh.models.actions import Callback'
    
done

