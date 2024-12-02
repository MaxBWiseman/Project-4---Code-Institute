# Tooter | A Reddit-style Site

#### Total time on this project - [![wakatime](https://wakatime.com/badge/user/d85da0fd-b442-4c33-98af-3ef622520fc1/project/91b3f0a1-e9d0-43bb-bd41-ce4137e84961.svg)](https://wakatime.com/badge/user/d85da0fd-b442-4c33-98af-3ef622520fc1/project/91b3f0a1-e9d0-43bb-bd41-ce4137e84961)

## Contents
* [Main Blurb](#main-blurb)
* [Target Audience](#target-audience)
* [User Experience](#user-experience)
* [Design Choices](#design-choices)
* [Features](#features)
    * [Future Implementations](#future-implementations)
* [Images](#images)
* [Testing](#testing)
    * [Testing Features](#testing-features)
    * [Testing UI](#testing-ui)
    * [User Testing](#user-testing)
* [Encountered Bugs](#encountered-bugs)
    * [](#)
    * [](#)
    * [](#)
* [My Algorithm's](#my-algorithms)
    * [](#)
    * [](#)
* [Languages](#languages-that-were-used-for-this-project)
    * [Other Libraries Used](#other-libraries-used)
* [Deployment](#deployment)
    * [Clone The Repository](#how-to-clone-this-repository)
    * [How To Create A Fork](#how-to-fork-this-repository)
* [Credits](#credits)
    * [Creator](#creator)
    * [Media](#media)
    * [Acknowledgements](#acknowledgements)
    * [Link to Production Deployment](#link-to-production-deployment)
    * [More Words from Developer](#more-words-from-developer)

## Main Blurb

Tooter is a Reddit-style platform designed to bring people together to share their thoughts, ideas, and interests. My mission was to create a dynamic community where users can engage in meaningful discussions, share content, and discover new topics that inspire them.


- **Blog Posting**
  - Create with a sleek Summernote editor
  - Like or dislike posts
  - Edit or delete your content whenever
  - Elevate your post with a custom banner image
  - Create your own categorys or use an existing one
- **Commenting**
  - Give your opinion on any post
  - Express yourself and attach a image
  - Like or dislike comments
  - Reply to any comment to have a nested thread
  - Edit or delete your comments whenever
  - Even group chat boards!
- **Groups**
  - Have a scoped interest? Make a group about it!
  - Admin your own group and have other like-minded tooters join
  - Group chat board
  - Tag your posts in a group to showcase it within the group
- **Profiles**
  - Uppon account creation you are given you own profile
  - Upload a profile image
  - Customize with a biography and optional location
  - View your Tooter statisitics such as, post grade or comment grade
  - View posts, comments and groups you have interacted with, or another user has interacted with
  - View other users profiles by clicking on their name


## Target Audience

Tooter is designed for individuals who are passionate about sharing their thoughts, ideas, and interests in a dynamic online community. Whether you are a blogger looking to create engaging content with a sleek Summernote editor, a commenter who enjoys expressing opinions and participating in nested discussions, or someone with a specific interest looking to create and manage groups, Tooter offers a platform for you. Our target audience includes:

- **Bloggers and Content Creators**: Those who want to create, edit, and share posts with custom banner images and categories.

- **Active Commenters**: Users who enjoy engaging in discussions, liking or disliking comments, and participating in group chat boards.

- **Interest-Based Group Enthusiasts**: Individuals who want to create and manage groups around specific interests, and tag posts to showcase within the group.

- **Profile Customizers**: Users who want to personalize their profiles with images, biographies, and view their interaction statistics.

- *Community Seekers*: People looking to connect with like-minded individuals, discover new topics, and engage in meaningful discussions.

Tooter aims to provide a comprehensive platform for all these users, fostering a vibrant and interactive community.


## User Experience

Tooter offers a seamless and engaging user experience designed to foster community interaction and content sharing. Users can easily create and manage their posts using the sleek Summernote editor, allowing for rich text formatting and the addition of custom banner images. The platform's intuitive interface makes it simple to like, dislike, edit, or delete content, ensuring users have full control over their contributions.

Commenting on posts is straightforward, with features that allow users to express their opinions, attach images, and engage in nested discussions. The ability to like or dislike comments and participate in group chat boards enhances the interactive experience.

Groups provide a space for users with specific interests to connect and collaborate. Creating and managing groups is user-friendly, and group admins can facilitate discussions through dedicated chat boards. Posts tagged within groups are showcased, making it easy for members to stay updated on relevant content.

Profiles on Tooter are customizable, allowing users to upload profile images, write biographies, and specify their location. Users can view their interaction statistics, such as post and comment grades, and explore the profiles of others by clicking on their names. This personalized touch helps users build their online identity and connect with like-minded individuals.


## Design Choices

The design choices for Tooter were made with the goal of creating an engaging and visually appealing platform that caters to a wide range of user preferences. One of the key design features is the inclusion of both day mode and night mode, allowing users to choose the interface that best suits their viewing preferences. This flexibility ensures that Tooter can attract and retain users who have different visual comfort needs.

### Day Mode
The day mode of Tooter features a bright and vibrant color scheme with contrasting green colors. This design choice was made to create a fresh and inviting look that enhances readability and user engagement during daytime use. The green color palette is not only visually appealing but also helps to create a sense of energy and activity on the platform.


### Night Mode
For users who prefer a darker interface, Tooter offers a night mode with dark blue colors. This mode is designed to reduce eye strain and provide a comfortable viewing experience in low-light environments. The dark blue color scheme creates a calm and focused atmosphere, making it ideal for users who engage with the platform during the evening or night.


### Consistent and Intuitive Design
Both day and night modes maintain a consistent layout and design elements to ensure a seamless user experience. The use of clear typography, intuitive navigation, and well-organized content helps users easily find and interact with the features they need. The sleek Summernote editor, customizable profiles, and interactive group chat boards are all designed to be user-friendly and visually cohesive.

### Accessibility Considerations
Accessibility was a key consideration in the design process. The contrasting color schemes in both modes ensure that text and interactive elements are easily distinguishable. Additionally, the platform includes features such as aria-labels for buttons and other interactive elements to support users who rely on assistive technologies.

### Extra
The switch that alternates between day and night on the top right of the navbar is made entireley from HTML and CSS, I learned this in a JSconfrernce about using less JavaScript.
The change between day and night modes is JavaScript, but the switch itself is pure HTML and CSS which I think is pretty cool. Source - https://www.youtube.com/watch?v=IP_rtWEMR0o&t=438s

#### Day mode
![Day mode layout](static/images/readme_images/final-look-ss1.png)

#### Night mode
![Night mode layout](static/images/readme_images/final-look-night-mode-ss1.png)


## Features

- **Blog Posting**
  - Create with a sleek Summernote editor
  - Like or dislike posts
  - Edit or delete your content whenever
  - Elevate your post with a custom banner image
  - Create your own categorys or use an existing one
- **Commenting**
  - Give your opinion on any post
  - Express yourself and attach a image
  - Like or dislike comments
  - Reply to any comment to have a nested thread
  - Edit or delete your comments whenever
  - Even group chat boards!
- **Groups**
  - Have a scoped interest? Make a group about it!
  - Admin your own group and have other like-minded tooters join
  - Group chat board
  - Tag your posts in a group to showcase it within the group
- **Profiles**
  - Uppon account creation you are given you own profile
  - Upload a profile image
  - Customize with a biography and optional location
  - View your Tooter statisitics such as, post grade or comment grade
  - View posts, comments and groups you have interacted with, or another user has interacted with
  - View other users profiles by clicking on their name

### Future Implementations

Tooter aims to continuously evolve and enhance the user experience by introducing new features and improvements. Here are some of the future implementations planned for the platform:

- **Video Posting**:

    Allow users to upload and share videos within their posts, providing a richer multimedia experience.
    Enable video playback directly within the platform, making it easy for users to engage with video content.

- **GIF Comments**:

    Introduce the ability to attach GIFs to comments, adding a fun and expressive way for users to interact.
    Provide a searchable GIF library to help users find the perfect GIF for their comment.

- **Navbar Search Bar**:

    Add a search bar to the navbar, allowing users to quickly find posts, groups, and users.
    Implement advanced search filters to help users narrow down their search results.

- **More Unique Widgets**:

    Develop and integrate additional widgets to enhance the user interface and provide more interactive elements.
    Examples include trending topics, recent activity feeds, and personalized content recommendations.

- **Add Friends to a Friends List**:

    Enable users to add other users as friends, creating a more connected and social experience.
    Provide notifications for friend requests and updates from friends.

- **More Group Admin Tools**:

    Expand the tools available to group admins, allowing for better management and moderation of groups.
    Features may include member management, content approval, and group analytics.


These future implementations are designed to further enrich the Tooter experience, making it a more versatile and engaging platform for all users. By continuously adding new features and improvements, Tooter aims to stay at the forefront of community-driven content sharing and interaction.

## Images

These images were taken throughout development and show the progression of this app
and to view the progress from wireframe to final design.
### Original wireframe

![alt text](static/images/readme_images/main_page_wireframe.png)

### Base template **before** final
![alt text](static/images/readme_images/base_templates_categorys.png)

![alt text](static/images/readme_images/base_templates_stage2.png)

![alt text](static/images/readme_images/base-templates_stage2-postview.png)


### Base template final

![alt text](static/images/readme_images/final-look-ss1.png)

![alt text](static/images/readme_images/final-look-night-mode-ss1.png)

![alt text](static/images/readme_images/base_template_final_ss3.png)

![alt text](static/images/readme_images/base_template_final_ss2.png)

![alt text](static/images/readme_images/base_template_final_ss1.png)

![alt text](static/images/readme_images/base_template_final_nightmode.png)



### Comments section before final

![alt text](static/images/readme_images/comment_on_posts1.png)

![alt text](static/images/readme_images/comment_on_posts2.png)

![alt text](static/images/readme_images/comment_on_posts3.png)

![alt text](static/images/readme_images/comment_on_posts4.png)

![alt text](static/images/readme_images/comment_on_posts5.png)



### 


### 


### 


### 



### 



### 



### 



### 



###



## Testing


### Testing features

| Test |Outcome  |
|--|--|
| | Pass|
| | Pass|
| | Pass|
| | Pass|
| | Pass|
| |Pass|
| |Pass|
| |Pass|
| |Pass|
| |Pass|

### Testing UI

| Test |Outcome  |
|--|--|
| |Pass|
| |Pass|

### User testing

#### 

| Test | Result |
|--|--|
|| 100%|
|| 100%|
| |100%|

## Encountered Bugs

### 

- 
#### Code Example


### 

- 

#### Code Example


### 

- 

#### Code Example


# My Algorithm's

## 

## 


## Languages that were used for this project

- ****: 

### Other Libraries Used

- ****:
- ****: 
- ****: 
- ****: .
- ****: 

## Deployment

### How I deployed my project


- ****
 - 
- ****
 - 
- ****
 -
- ****
 -  

Deployment link -

### How to clone this repository

To clone this repository, use the following command:

git clone https://github.com/yourusername/Event-Hoarder.git


### How to fork this repository

To fork this repository, follow these steps:

Navigate to the repository on GitHub.

Click the "Fork" button at the top right of the page.

Select your GitHub account to fork the repository to.

## Credits

### Creator
This project was created by me, Max Wiseman

### Media


### Acknowledgements


### Link to production deployment