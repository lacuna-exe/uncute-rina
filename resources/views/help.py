import discord
from resources.customs.help import HelpPage, generate_help_page_embed
from resources.customs.bot import Bot
from resources.modals.generics import SingleLineModal
import random # for random help page jump page number placeholder

from resources.views.generics import PageView, create_simple_button

class HelpPageView(PageView):
    async def update_page(self, itx: discord.Interaction, view: PageView) -> None:
        page_key = list(self.pages)[self.page]
        embed = generate_help_page_embed(self.pages[page_key], page_key, self.client)
        await itx.response.edit_message(
            embed=embed,
            view=view
        )

    # region buttons
    @discord.ui.button(emoji="📋", style=discord.ButtonStyle.gray)
    async def go_to_index(self, itx: discord.Interaction, _: discord.ui.Button):
        self.page = 1 # page 2, but index 1
        self.update_button_colors()
        await self.update_page(itx, self)

    
    @discord.ui.button(emoji="🔢", style=discord.ButtonStyle.gray)
    async def jump_to_page(self, itx: discord.Interaction, _: discord.ui.Button):
        help_page_indexes = list(self.pages)
        jump_page_modal = SingleLineModal(
            "Jump to a help page",
            "What help page do you want to jump to?",
            placeholder=str(random.choice(help_page_indexes))
        )
        await itx.response.send_modal(jump_page_modal)
        await jump_page_modal.wait()
        if jump_page_modal.itx == None:
            return
        
        try:
            if not jump_page_modal.question_text.value.isnumeric():
                raise ValueError 
            page_guess = int(jump_page_modal.question_text.value)
        except ValueError:
            await itx.response.send_message("Error: Invalid number.\n"
                                            "\n"
                                            "This button lets you jump to a help page (number). To see what kinds of help pages there are, go to the index page (page 2, or click the 📋 button).\n"
                                            "An example of a help page is page 3: `Utility`. To go to this page, you can either use the previous/next buttons (◀️ and ▶️) to navigate there, or click the 🔢 button: This button opens a modal.\n"
                                            "In this modal, you can put in the page number you want to jump to. Following from our example, if you type in '3', it will bring you to page 3; `Utility`.\n"
                                            "Happy browsing!", ephemeral=True)
            return
        
        if page_guess not in help_page_indexes:
            # find closest pages to the given number
            if page_guess > help_page_indexes[-1]:
                relative_page_location_details = f" (nearest pages to `{page_guess}` are `{help_page_indexes[-1]}` and `{help_page_indexes[0]}`)"
            elif page_guess < help_page_indexes[0]:
                relative_page_location_details = f" (nearest pages to `{page_guess}` are `{help_page_indexes[0]}` and `{help_page_indexes[-1]}`)"
            else: # page is between two other pages
                min_index = page_guess
                max_index = page_guess
                while min_index not in help_page_indexes:
                    min_index -= 1
                while max_index not in help_page_indexes:
                    max_index += 1
                relative_page_location_details = f" (nearest pages to `{page_guess}` are `{min_index}` and `{max_index}`)"
            await itx.response.send_message(f"Error: Number invalid. Please go to a valid help page" + relative_page_location_details + ".", ephemeral=True)
            return
        
        self.page = list(self.pages).index(page_guess)
        self.update_button_colors()
        await self.update_page(jump_page_modal.itx, self)
    # endregion buttons

    def __init__(self, client: Bot, first_page_key: int, page_dict: dict[int, HelpPage]) -> None:
        self.client = client
        self.pages = page_dict
        first_page_index = list(self.pages).index(first_page_key)
        super().__init__(first_page_index, len(self.pages)-1, self.update_page)
        self._children.append(self._children.pop(1))
