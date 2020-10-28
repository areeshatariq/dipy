.. _reconstruction_flow:

==============
Reconstruction
==============

This tutorial walks through the steps to perform reconstruction using DIPY.
Multiple registration methods are available in DIPY.

You can try these methods using your own data; we will be using the data in DIPY.
You can check how to :ref:`fetch the DIPY data<data_fetch>`.

-----------------------------------
Constrained Spherical Deconvolution
-----------------------------------

This method is mainly useful with datasets with gradient directions acquired on a
spherical grid.

The basic idea with this method is that if we could estimate the response function
of a single fiber then we could deconvolve the measured signal and obtain the
underlying fiber distribution.

In this way, the reconstruction of the fiber orientation distribution function
(fODF) in CSD involves two steps:

* Estimation of the fiber response function
* Use the response function to reconstruct the fODF

----------------------------------
Mean Apparent Propagator (MAP)-MRI
----------------------------------

The MAP-MRI basis allows for the computation of directional indices, such as
the Return To the Axis Probability (RTAP), the Return To the Plane Probability
(RTPP), and the parallel and perpendicular Non-Gaussianity.

The estimation of analytical Orientation Distribution Function (ODF) and a
variety of scalar indices from noisy DWIs requires that the fitting of the ]
MAPMRI basis is regularized.

------------------------
Diffusion Tensor Imaging
------------------------

The diffusion tensor model is a model that describes the diffusion within a
voxel. First proposed by Basser and colleagues [Basser1994]_, it has been very
influential in demonstrating the utility of diffusion MRI in characterizing the
micro-structure of white matter tissue and of the biophysical properties of
tissue, inferred from local diffusion properties and it is still very commonly
used.

The diffusion tensor models the diffusion signal as:

.. math::

    \frac{S(\mathbf{g}, b)}{S_0} = e^{-b\mathbf{g}^T \mathbf{D} \mathbf{g}}

Where $\mathbf{g}$ is a unit vector in 3 space indicating the direction of
measurement and b are the parameters of measurement, such as the strength and
duration of diffusion-weighting gradient. $S(\mathbf{g}, b)$ is the
diffusion-weighted signal measured and $S_0$ is the signal conducted in a
measurement with no diffusion weighting. $\mathbf{D}$ is a positive-definite
quadratic form, which contains six free parameters to be fit. These six
parameters are:

.. math::

   \mathbf{D} = \begin{pmatrix} D_{xx} & D_{xy} & D_{xz} \\
                       D_{yx} & D_{yy} & D_{yz} \\
                       D_{zx} & D_{zy} & D_{zz} \\ \end{pmatrix}

This matrix is a variance/covariance matrix of the diffusivity along the three
spatial dimensions. Note that we can assume that diffusivity has antipodal
symmetry, so elements across the diagonal are equal. For example:
$D_{xy} = D_{yx}$. This is why there are only 6 free parameters to estimate
here.

--------------------------
Diffusion Kurtosis Imaging
--------------------------

The diffusion kurtosis model is an expansion of the diffusion tensor model. In
addition to the diffusion tensor (DT), the diffusion kurtosis model quantifies
the degree to which water diffusion in biological tissues is non-Gaussian using
the kurtosis tensor (KT) [Jensen2005]_.

Measurements of non-Gaussian diffusion from the diffusion kurtosis model are of
interest because they can be used to charaterize tissue microstructural
heterogeneity [Jensen2010]_. 

Moreover, DKI can be used to:

* Derive concrete biophysical parameters, such as the density of axonal fibers and diffusion tortuosity [Fierem2011]_

* Resolve crossing fibers in tractography and to obtain invariant rotational measures not limited to well-aligned fiber populations [NetoHe2015]_.

--------------------
Constant Solid Angle
--------------------


-----------------------------------
Intravoxel incoherent motion (IVIM)
-----------------------------------

The intravoxel incoherent motion (IVIM) model describes diffusion
and perfusion in the signal acquired with a diffusion MRI sequence
that contains multiple low b-values. The IVIM model can be understood
as an adaptation of the work of Stejskal and Tanner [Stejskal65]_
in biological tissue, and was proposed by Le Bihan [LeBihan84]_.
The model assumes two compartments: a slow moving compartment,
where particles diffuse in a Brownian fashion as a consequence of thermal
energy, and a fast moving compartment (the vascular compartment), where
blood moves as a consequence of a pressure gradient. In the first compartment,
the diffusion coefficient is $\mathbf{D}$ while in the second compartment, a
pseudo diffusion term $\mathbf{D^*}$ is introduced that describes the
displacement of the blood elements in an assumed randomly laid out vascular
network, at the macroscopic level. According to [LeBihan84]_,
$\mathbf{D^*}$ is greater than $\mathbf{D}$.

References
----------

.. [Basser1994] Basser PJ, Mattielo J, LeBihan (1994). MR diffusion tensor
                spectroscopy and imaging.

.. [Jensen2005] Jensen JH, Helpern JA, Ramani A, Lu H, Kaczynski K (2005).
                Diffusional Kurtosis Imaging: The Quantification of
                Non_Gaussian Water Diffusion by Means of Magnetic Resonance
                Imaging. Magnetic Resonance in Medicine 53: 1432-1440
                
.. [Jensen2010] Jensen JH, Helpern JA (2010). MRI quantification of
                non-Gaussian water diffusion by kurtosis analysis. NMR in
                Biomedicine 23(7): 698-710

.. [Fierem2011] Fieremans E, Jensen JH, Helpern JA (2011). White matter
                characterization with diffusion kurtosis imaging. NeuroImage
                58: 177-188

.. [NetoHe2015] Neto Henriques R, Correia MM, Nunes RG, Ferreira HA (2015).
                Exploring the 3D geometry of the diffusion kurtosis tensor -
                Impact on the development of robust tractography procedures and
                novel biomarkers, NeuroImage 111: 85-99

.. [Stejskal65] Stejskal, E. O.; Tanner, J. E. (1 January 1965).
                "Spin Diffusion Measurements: Spin Echoes in the Presence
                of a Time-Dependent Field Gradient". The Journal of Chemical
                Physics 42 (1): 288. Bibcode: 1965JChPh..42..288S.
                doi:10.1063/1.1695690.

.. [LeBihan84] Le Bihan, Denis, et al. "Separation of diffusion
               and perfusion in intravoxel incoherent motion MR
               imaging." Radiology 168.2 (1988): 497-505.