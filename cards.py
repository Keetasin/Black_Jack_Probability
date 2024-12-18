### Import packages
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt  # เพิ่มการแสดงผลทีละภาพ

### Constants ###
# Debugging
DEBUG_MODE = False
WRITE_IMAGES = False

# Card dimensions
CARD_MAX_AREA = 1000000
CARD_MIN_AREA = 70000

CARD_MAX_PERIM = 1000
CARD_MIN_PERIM = 200

RANK_HEIGHT = 125
RANK_WIDTH = 70

CARD_WIDTH = 200
CARD_HEIGHT = 300

# Polymetric approximation accuracy scaling factor
POLY_ACC_CONST = 0.02

# Matching algorithms
HU_MOMENTS = 0
TEMPLATE_MATCHING = 1
MAX_MATCH_SCORE = 3000

### Structures ###
class Rank:
    """Structure to store information about each card rank."""

    def __init__(self, name="", img=None, contour=None, value=0):
        self.name = name
        self.img = img if img is not None else []
        self.contour = contour if contour is not None else []
        self.value = value

class Card:
    """Structure to store information about cards in the camera image."""

    def __init__(self):
        self.contour = []  # Contour of card
        self.corner_pts = []  # Corner points of card
        self.center = []  # Center point of card
        self.img = []  # Top-down flattened image of the card
        self.rank_img = []  # Thresholded, sized image of card's rank
        self.rank_contour = []  # Contour of the rank
        self.best_rank_match = "Unknown"  # Best matched rank
        self.rank_score = 0  # Difference between rank image and best matched train rank image
        self.value = 0  # Numerical value of the rank

 

    def process_card(self, image):
        """Process and flatten the card image to extract rank."""
        x, y, w, h = cv2.boundingRect(self.contour)
        self.center = np.mean(self.corner_pts, axis=0).astype(int).tolist()[0]

        # Step 1: Flatten the card to a top-down view
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.img = flattener(gray, self.corner_pts, w, h)

        # Display the flattened card
        # plt.imshow(self.img, cmap='gray')
        # plt.title("Top-Down View of Card")
        # plt.show()

        # Step 2: Crop the top-left corner
        rank_img = self.img[0:55 , 0:35]         # cropppp
        pad_value = np.median(rank_img)
        rank_img_padded = np.pad(rank_img, 5, 'constant', constant_values=pad_value)

        _, thresh = cv2.threshold(rank_img_padded, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.bitwise_not(thresh)

        # Display the cropped and thresholded top-left corner
        # plt.imshow(thresh, cmap='gray')
        # plt.title("Cropped Top-Left Corner for Rank")
        # plt.show()

        # Step 3: Extract rank contour
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if contours:
            self.rank_contour = contours[0]
            x1, y1, w1, h1 = cv2.boundingRect(contours[0])
            rank_crop = thresh[y1:y1 + h1, x1:x1 + w1]
            self.rank_img = cv2.resize(rank_crop, (RANK_WIDTH, RANK_HEIGHT))

            # Display the final rank image for matching
            # plt.imshow(self.rank_img, cmap='gray')
            # plt.title("Final Rank Image for Matching")
            # plt.show()



    def match_rank(self, all_ranks, match_method, last_cards):
        # Ensure the rank image is in grayscale format
        if isinstance(self.rank_img, np.ndarray):  # Check if rank_img is a NumPy array
            if len(self.rank_img.shape) == 3:  # If image is BGR
                self.rank_img = cv2.cvtColor(self.rank_img, cv2.COLOR_BGR2GRAY)
        else:
            print("Error: Rank image is not a NumPy array.")
            return  # Add a return statement to prevent further processing

        # Match the rank using templates or HU moments
        match_scores = []
        for rank in all_ranks:
            if not isinstance(rank.img, np.ndarray):
                raise ValueError("Rank images must be NumPy arrays.")
            
            # Ensure comparison images are grayscale
            rank_img_compare = rank.img  # Already in grayscale
            if rank_img_compare is None:
                continue
            
            if match_method == HU_MOMENTS:
                match_scores.append(cv2.matchShapes(self.contour, rank.contour, 1, 0.0))
            elif match_method == TEMPLATE_MATCHING:
                diff_img = cv2.absdiff(self.rank_img, rank_img_compare)
                match_scores.append(int(np.sum(diff_img) / 255))
        
        ind = np.argmin(match_scores)
        self.rank_score = match_scores[ind]

        if self.rank_score < MAX_MATCH_SCORE:
            self.best_rank_match = all_ranks[ind].name
            self.value = all_ranks[ind].value

        # Reduce flickering using last matched cards
        if self.best_rank_match == "Unknown" and last_cards:
            for last_card in last_cards:
                if np.allclose(self.center, last_card.center, atol=10):
                    self.best_rank_match = last_card.best_rank_match
                    self.value = last_card.value

def detect(image, rank_path, last_cards):
    """Detects cards in an image and returns a list of processed card objects."""
    ranks = load_ranks(rank_path)
    cards = find_cards(image)

    for card in cards:
        card.process_card(image)
        card.match_rank(ranks, TEMPLATE_MATCHING, last_cards)
    return cards

def display(image, cards):
    """Draw detected cards with their best rank matches and corner points on the image."""
    for card in cards:
        # Draw the main card contour
        color = (0, 255, 0) if card.best_rank_match != "Unknown" else (0, 0, 255)
        cv2.drawContours(image, [card.contour], 0, color, 2)
        
        # Draw the corner points
        for pt in card.corner_pts:
            cv2.circle(image, tuple(pt[0]), 5, (255, 0, 0), -1)

        # Draw the bounding box
        x, y, w, h = cv2.boundingRect(card.contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # Display the card rank
        text_pos = (card.center[0] - 20, card.center[1])
        cv2.putText(image, card.best_rank_match, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    return image

def find_cards(image):
    """Find potential card contours in the input image."""
    cards = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for cnt in sorted_contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, POLY_ACC_CONST * peri, True)
            if CARD_MIN_AREA < cv2.contourArea(cnt) < CARD_MAX_AREA and len(approx) == 4:
                new_card = Card()
                new_card.contour = cnt
                new_card.corner_pts = approx
                cards.append(new_card)
    return cards

def load_ranks(path):
    """Load rank templates and store them as Rank objects."""
    rank_names = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
    rank_values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    ranks = []

    for i, name in enumerate(rank_names):
        img_path = os.path.join(path, f"{name}.png")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Error loading rank image: {img_path}")  # Ensure grayscale loading
            continue  # Skip if the image is not found
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        ranks.append(Rank(name, img, contours[0], rank_values[i]))
    return ranks


def flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=2)
    rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
    diff = np.diff(pts, axis=-1)
    rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]

    dst = np.array([[0, 0], [CARD_WIDTH - 1, 0], [CARD_WIDTH - 1, CARD_HEIGHT - 1], [0, CARD_HEIGHT - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (CARD_WIDTH, CARD_HEIGHT))

def is_card_inside_rect(card, rect):
    """ตรวจสอบว่าไพ่ตั้งอยู่ภายในกรอบสี่เหลี่ยมหรือไม่"""
    x1, y1, x2, y2 = rect  # (top-left-x, top-left-y, bottom-right-x, bottom-right-y)
    cx, cy = card.center  # ศูนย์กลางของไพ่
    return x1 <= cx <= x2 and y1 <= cy <= y2


def calculate_total_value(cards):
    """Calculate the total value of all detected cards."""
    total_value = sum(card.value for card in cards if card.value > 0)
    return total_value


def process_folder(input_folder, output_folder, rank_path, last_cards=[]):
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define rectangle for filtering (x1, y1, x2, y2)
    filter_rect_player = (500,600, 1500, 1100)  # กรอบสำหรับผู้เล่น
    filter_rect_dealer = (500,50, 1500, 520)  # กรอบสำหรับดีลเลอร์

    # Loop through all images in the input folder
    for image_filename in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_filename)

        # Read the input image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Cannot read image from {image_path}")
            continue

        # Detect cards in the image
        cards = detect(image, rank_path, last_cards)

        # Filter cards inside the rectangle
        filtered_cards_players = [card for card in cards if is_card_inside_rect(card, filter_rect_player)]
        filtered_cards_dealer = [card for card in cards if is_card_inside_rect(card, filter_rect_dealer)]
        
        # Calculate total value of filtered cards
        total_value_players = calculate_total_value(filtered_cards_players)
        total_value_dealer = calculate_total_value(filtered_cards_dealer)

        if "round" in image_filename.lower():
            # Display the rectangle on the image
            cv2.rectangle(image, (filter_rect_player[0], filter_rect_player[1]), (filter_rect_player[2], filter_rect_player[3]), (255, 0, 0), 2)
            cv2.rectangle(image, (filter_rect_dealer[0], filter_rect_dealer[1]), (filter_rect_dealer[2], filter_rect_dealer[3]), (255, 0, 0), 2)

            # Add text showing total value of cards in each rectangle
            cv2.putText(image, f"Player: {total_value_players}", 
                        (filter_rect_player[2]-150, filter_rect_player[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, f"Dealer: {total_value_dealer}", 
                        (filter_rect_dealer[2]-150, filter_rect_dealer[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if "post" in image_filename.lower():
            if (total_value_dealer == total_value_players) or (total_value_players>21 and total_value_dealer>21):
                cv2.putText(image, "Draw", (200,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            elif ((total_value_players > total_value_dealer)and total_value_players < 22) or (total_value_dealer>21):
                cv2.putText(image, "Player Win", (10,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            elif ((total_value_dealer > total_value_players)and total_value_dealer < 22) or (total_value_players>21):
                cv2.putText(image, "Dealer Win", (10,600),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)

            if total_value_players == 21:
                    cv2.putText(image, "Black Jack", (10,900),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            if total_value_dealer == 21:
                    cv2.putText(image, "Black Jack", (10,200),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)

            if total_value_players > 21:
                    cv2.putText(image, "Bust", (10,900),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            if total_value_dealer > 21:
                    cv2.putText(image, "Bust", (10,200),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)

        # Display the image with detected cards
        result_image = display(image, cards)

        # Save the result in the output folder
        output_path = os.path.join(output_folder, image_filename)
        cv2.imwrite(output_path, result_image)
        print('*' * 10)
        print(image_filename)
        print(f"players: {total_value_players}")
        print(f"dealer: {total_value_dealer}")
        print([card.value for card in filtered_cards_players])
        print([card.value for card in filtered_cards_dealer])
        print(f"Processed: {image_filename}")


if __name__ == "__main__":
    input_folder = 'images'
    output_folder = 'images/detected'
    rank_path = 'template'  # Directory containing rank images (Ace.png, Two.png, etc.)
    process_folder(input_folder, output_folder, rank_path)


