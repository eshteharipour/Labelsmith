import json
import os

import pandas as pd
import streamlit as st
from PIL import Image
from prod2vec.dataset.settings import LCSCIseeCLip


class ImageCleaner:
    def __init__(self, data_file: str, state_file: str, page_size: int = 100):
        self.data_file = data_file
        self.state_file = state_file
        self.page_size = page_size

        # Initialize state
        self.load_data()
        self.load_state()

        # Initialize session state if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = self.last_page
        if "view_mode" not in st.session_state:
            st.session_state.view_mode = "grid"
        if "selected_images" not in st.session_state:
            st.session_state.selected_images = self.selected_images

    def load_data(self):
        """Load and validate the dataset"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Dataset file '{self.data_file}' not found.")

        self.df = pd.read_csv(
            self.data_file, sep="\t", dtype=object, keep_default_na=False
        )
        self.total_pages = len(self.df) // self.page_size + (
            1 if len(self.df) % self.page_size > 0 else 0
        )

    def load_state(self):
        """Load previous state from file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.selected_images = set(state.get("selected_images", []))
                self.last_page = state.get("last_page", 0)
        else:
            self.selected_images = set()
            self.last_page = 0

    def save_state(self):
        """Save current state to file"""
        state = {
            "selected_images": list(st.session_state.selected_images),
            "last_page": st.session_state.current_page,
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)

    def get_page_data(self):
        """Get data for current page"""
        start_idx = st.session_state.current_page * self.page_size
        end_idx = start_idx + self.page_size
        return self.df.iloc[start_idx:end_idx]

    def load_image(self, image_path):
        """Safely load an image with error handling"""
        try:
            image = Image.open(image_path)
            return image
        except Exception as e:
            st.error(f"Error loading image {image_path}: {str(e)}")
            return None

    def render_navigation(self):
        """Render navigation controls"""
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
                st.session_state.current_page = max(
                    0, st.session_state.current_page - 1
                )
                self.save_state()
                st.rerun()

        with col3:
            st.write(f"Page {st.session_state.current_page + 1} of {self.total_pages}")

        with col5:
            if st.button(
                "Next ➡️",
                disabled=st.session_state.current_page >= self.total_pages - 1,
            ):
                st.session_state.current_page = min(
                    self.total_pages - 1, st.session_state.current_page + 1
                )
                self.save_state()
                st.rerun()

    def render_controls(self):
        """Render view controls and navigation"""
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("Row View", type="secondary"):
                st.session_state.view_mode = "row"

        with col2:
            if st.button("Grid View", type="secondary"):
                st.session_state.view_mode = "grid"

        with col3:
            if st.button("View Selected Images"):
                st.session_state.show_selected = True

    def render_grid_item(self, row):
        """Render a single grid item"""
        col = st.columns(1)[0]
        with col:
            image = self.load_image(row["path"])
            if image:
                st.image(image, use_container_width=True)

            # Title with tooltip
            st.markdown(
                f"<div title='{row['name']}'>{row['name'][:20]}...</div>",
                unsafe_allow_html=True,
            )

            # Optional metadata
            if "source" in row and row["source"]:
                st.caption(f"Source: {row['source']}")
            if "site_id" in row and row["site_id"]:
                st.caption(f"Site ID: {row['site_id']}")

            # Selection button
            is_selected = row["path"] in st.session_state.selected_images
            if st.button(
                "Deselect" if is_selected else "Select",
                key=f"btn_{row.name}",
                type="primary" if is_selected else "secondary",
            ):
                if is_selected:
                    st.session_state.selected_images.remove(row["path"])
                else:
                    st.session_state.selected_images.add(row["path"])
                self.save_state()
                st.rerun()

    def render_row_item(self, row):
        """Render a single row item"""
        col1, col2, col3 = st.columns([2, 6, 2])

        with col1:
            image = self.load_image(row["path"])
            if image:
                st.image(image, width=150)

        with col2:
            st.write(row["name"])
            if "source" in row and row["source"]:
                st.caption(f"Source: {row['source']}")
            if "site_id" in row and row["site_id"]:
                st.caption(f"Site ID: {row['site_id']}")

        with col3:
            is_selected = row["path"] in st.session_state.selected_images
            if st.button(
                "Deselect" if is_selected else "Select",
                key=f"btn_{row.name}",
                type="primary" if is_selected else "secondary",
            ):
                if is_selected:
                    st.session_state.selected_images.remove(row["path"])
                else:
                    st.session_state.selected_images.add(row["path"])
                self.save_state()
                st.rerun()

    def render_selected_images(self):
        """Render the selected images view"""
        if st.button("Back to Main View"):
            st.session_state.show_selected = False
            st.rerun()

        st.header("Selected Images")

        selected_df = self.df[self.df["path"].isin(st.session_state.selected_images)]
        if len(selected_df) == 0:
            st.write("No images selected")
            return

        cols = st.columns(4)
        for idx, (_, row) in enumerate(selected_df.iterrows()):
            with cols[idx % 4]:
                self.render_grid_item(row)

    def render_main_view(self):
        """Render the main view with current page data"""
        self.render_controls()
        self.render_navigation()

        page_data = self.get_page_data()

        if st.session_state.view_mode == "grid":
            cols = st.columns(4)
            for idx, (_, row) in enumerate(page_data.iterrows()):
                with cols[idx % 4]:
                    self.render_grid_item(row)
        else:
            for _, row in page_data.iterrows():
                self.render_row_item(row)
                st.divider()

    def run(self):
        """Main application entry point"""
        st.title("Image Dataset Cleaner")

        if (
            hasattr(st.session_state, "show_selected")
            and st.session_state.show_selected
        ):
            self.render_selected_images()
        else:
            self.render_main_view()


def main():
    # Configuration
    DATA_FILE = LCSCIseeCLip.dataset_path
    STATE_FILE = "artifacts/state.json"
    PAGE_SIZE = 100

    # Create state file directory if it doesn't exist
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    # Initialize and run the application
    app = ImageCleaner(DATA_FILE, STATE_FILE, PAGE_SIZE)
    app.run()


if __name__ == "__main__":
    # st.write(st.__version__)
    main()
