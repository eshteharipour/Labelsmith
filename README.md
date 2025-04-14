
```bash
pip install fastapi uvicorn python-multipart pandas
cd frontend
npm install
npm run build
uvicorn main:app --reload
python -m cleaner.classifier
uvicorn backend.main:app --reload
uvicorn backend.main:app --reload --log-level debug
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

uvicorn cleaner.classifier:app --reload --workers 8
uvicorn cleaner.matcher:app --reload --workers 8
uvicorn cleaner.viewer:app --reload --workers 8
uvicorn cleaner.cluster:app --reload --workers 8

# no need for the following, use npm run dev.
npm run build && npm run preview


# vite
npm run dev
# http://localhost:5173/

# if you open http://localhost:8000/ routing worn't work correctly!
```

Prompt:

```txt
This Dash app has lots of bugs but it's supposed to provide interface for cleaning a csv with lots of images and storing bad images in a state file i tried mutiple times with you to fix the bugs but you couldn't so i want you to rewrite this in a library of your choosing that you understand better and are more proffesional in it and the programming language has to be python

make sure your code has all these features of the previous code which was made with this prompt:

i want a dash app with python to clean a lot of bad images out of a dataset, so the csv dataset has a title and path col the path is the image path on file system i want the dash app to have pagination, because the csv is huge with 2mil records, so i want each page to have 100 rows (configurable) shown, i want to be able to click on a row and the path of that row's image must be stored to a list so i can know which images were bad, i want to see the image be highlighted when I select, and when I deselect i want it removed from the list, if it was added now or previously, it should store each interaction to a json as state it should read this state on start up and load the last page i was on, it should be able to hightlight previously selected images based on this csv i wanna be able to have different views of my imagesm, one is row based which means name and image on each rown and next row is next item from csv the over view i want is like file explorer view where each image is an icon on a grid (configurable size of grid with padding between images) and the title should be displayed below the image but it should be truncated if very long and on hover on title it should display full title, also i wanna see the path of each image when i hover my mouse iver images. i thought dash can get this done easier with less lines of code and more efficient but you can suggest other libraries or if you know already made libraries like label sutduio or labelimg or whatver. first mak a list of all features i need and the description of the problem then suggest solutions of libraries or write code thanks

I want new features on my app: a current_page/total_page before next/previous a new button on top of page that will route me to another page which will show selected images from json state file, it should load and display selected images and the same button on the new page should exist to take me back to previous page there's also a row called source and a row called site_id in my df if they are not none please display them. in both views there's also a bug where when i click grid view (when changing view to the other view) it does not take effect until i click next/previous buttons
```
