def load_reviews():
    reviews = []
    try:
        with open("data/review.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 4:
                    reviews.append({
                        "user": parts[0],
                        "dish": parts[1],
                        "comment": parts[2],
                        "rating": parts[3]
                    })
    except FileNotFoundError:
        pass
    return reviews


def save_reviews(reviews):
    with open("data/review.txt", "w") as f:
        for review in reviews:
            f.write(f"{review['user']}|||{review['dish']}|||{review['comment']}|||{review['rating']}\n")


def dishes_review(current_user):
    if not current_user:
        print("Please login first")
        return current_user

    reviews = load_reviews()
    user_reviews = [r for r in reviews if r["user"] == current_user]

    while True:
        print(f"\nReviews by {current_user}:")
        if not user_reviews:
            print("(No reviews yet)")
        else:
            for idx, review in enumerate(user_reviews, 1):
                print(f"{idx}. {review['dish']}: {review['comment']} ({review['rating']}/5)")

        print("\n1. Add Review")
        print("2. Delete Review")
        print("3. Back")
        choice = input("Choose (1-3): ")

        if choice == "1":
            dish = input("Dish name: ").strip()
            comment = input("Your review: ").strip()
            while True:
                rating = input("Rating (1-5): ").strip()
                if rating.isdigit() and 1 <= int(rating) <= 5:
                    break
                print("Invalid rating! Enter 1-5.")

            reviews.append({
                "user": current_user,
                "dish": dish,
                "comment": comment,
                "rating": rating
            })
            save_reviews(reviews)
            print("Review added successfully!")
            return current_user

        elif choice == "2":
            if not user_reviews:
                print("No reviews to delete!")
                continue

            try:
                idx = int(input("Enter review number to delete: ")) - 1
                if 0 <= idx < len(user_reviews):
                    reviews = [r for r in reviews if r != user_reviews[idx]]
                    save_reviews(reviews)
                    print("Review deleted!")
                else:
                    print("Invalid number!")
            except ValueError:
                print("Please enter a valid number!")

        elif choice == "3":
            return current_user